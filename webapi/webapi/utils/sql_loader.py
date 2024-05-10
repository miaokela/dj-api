# Description: jinja2实现动态sql
import os
import threading
import typing

import yaml
import jinja2


class g:
    sql_dict = {}


class SingletonType(type):
    _instance_lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with SingletonType._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = super(SingletonType, cls).__call__(*args, **kwargs)
        return cls._instance


class SqlLoader(metaclass=SingletonType):
    """
    根据sql_id来读取指定yml文件下对应key的sql
    """
    SQL_FILE_PATH = os.path.join(
        os.path.dirname(
            os.path.dirname(os.path.realpath(__file__))
        ),
        'sql'
    )

    def __init__(self):
        self.sql_data = SqlLoader.get_sql_data(self.SQL_FILE_PATH)

    @classmethod
    def preload_all_sqls(cls):
        """
        Preload all sqls into memory
        """
        for _path, _, files in os.walk(cls.SQL_FILE_PATH):
            if os.path.samefile(_path, cls.SQL_FILE_PATH):  # root path
                for _f in files:
                    if not _f.endswith('.yml'):
                        continue
                    c_file = os.path.join(_path, _f)
                    c_file_name = _f.replace('.yml', '')

                    try:
                        with open(c_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            sql_dict = yaml.load(content, Loader=yaml.FullLoader)
                            if not sql_dict:
                                continue

                            for _k in sql_dict.keys():
                                _sql_id = '%s.%s' % (c_file_name, _k)
                                g.sql_dict[_sql_id] = sql_dict[_k]
                    except:
                        print('错误文件: {}'.format(c_file_name))
                continue

            relative_path = _path.replace(cls.SQL_FILE_PATH, '')

            if relative_path.startswith(os.sep):
                relative_path = relative_path[1:]
            if relative_path.endswith(os.sep):
                relative_path = relative_path[:-1]

            prefix_sql_id = relative_path.replace(os.sep, '.')

            for _f in files:
                c_file = os.path.join(_path, _f)
                c_file_name = _f.replace('.yml', '')
                if not _f.endswith('.yml'):
                    continue
                
                with open(c_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    sql_dict = yaml.load(content, Loader=yaml.FullLoader)
                    if not sql_dict:
                        continue

                    for _k in sql_dict.keys():
                        _sql_id = '%s.%s.%s' % (prefix_sql_id, c_file_name, _k)
                        g.sql_dict[_sql_id] = sql_dict[_k]

        return True

    def get_sql(self, sql_id: str) -> str:
        if not hasattr(g, 'sql_dict'):
            g.sql_dict = {}
        if sql_id in g.sql_dict:
            return g.sql_dict[sql_id]
        else:
            sql = self.__load_sql(sql_id)
            g.sql_dict[sql_id] = sql
            return sql

    def __load_sql(self, sql_id: str) -> str:
        # 根据传入的 sql_id 找到对应的文件名和sql_id前缀
        sql_id_prefix = '.'.join(sql_id.split('.')[:-1])
        c_file = self.sql_data.get(sql_id_prefix)
        if not c_file:
            raise Exception('sql file not found')
        with open(c_file, 'r', encoding='utf-8') as f:
            content = f.read()
            sql_dict = yaml.load(content, Loader=yaml.FullLoader)
            if not sql_dict:
                raise Exception('sql file is empty')
            # 根据sql_id获取sql
            sql_keys = sql_id.split('.')
            if len(sql_keys) > 1:
                sql_key = sql_keys[-1]
            else:
                raise Exception('sql_id pattern error')
            sql = sql_dict.get(sql_key)
            if not sql:
                raise Exception('sql_id: %s not found' % sql_id)
        return sql

    @staticmethod
    def get_files(path: str) -> typing.List[str]:
        file_list = []
        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            if os.path.isdir(file_path):
                file_list.extend(SqlLoader.get_files(file_path))
            else:
                file_list.append(file_path)
        return file_list

    @staticmethod
    def get_sql_data(path: str) -> typing.Dict[str, str]:
        file_list = SqlLoader.get_files(path)
        return {
            file.replace(
                path if path.endswith(os.sep) else path + os.sep, '')
            .replace('.yml', '').replace(os.sep, '.'): file
            for file in file_list
        }

    def preload_sql(self, sql_id: str, options: typing.Dict = None) -> str:
        """
        预加载sql

        添加分页功能:将options中,pageNum与pageSize转化成limit与offset
            {
                "pageNum": 1,
                "pageSize": 20,
            }
        :param sql_id: 查询sql的id
        :param options: 动态添加参数字典
        :return:
        """
        if not options:
            options = {}

        c_sql = self.get_sql(sql_id)

        page_num = options.get('pageNum')
        page_size = options.get('pageSize')

        if page_num:
            del options['pageNum']
        if page_size:
            del options['pageSize']

        if any([page_num, page_size]):
            page_num = page_num if page_num else 1
            options['limit'] = page_size if page_size else 10  # 默认10条
            options['offset'] = (page_num - 1) * options['limit']

            c_sql += """
            {% if limit and not offset %}
                LIMIT {{ limit }}
                {% elif limit and offset %}
                LIMIT {{ offset }},{{ limit }}
            {% endif %}
            """

        return jinja2.Template(c_sql).render(options) if options else c_sql


sql_loader = SqlLoader()

if __name__ == '__main__':
    ret = sql_loader.preload_sql("home_page.sensor.selectAll", options={"equipment_id": 1})
    print(ret)
