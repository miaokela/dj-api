import copy
import typing

from django.db import connection

from ..utils.sql_loader import sql_loader


class DBData(dict):
    """
    Set data or get data with point and bracket.
    """
    def __getattr__(self, key):
        return self.get(key, None)

    def __setattr__(self, key, value):
        if key in self.__dict__:
            self.__dict__[key] = value
        else:
            self[key] = value


class DBHelper(object):

    print_msg = True
    page_param = 'page'
    page_size_param = 'page_size'
    sql_injection_keywords = ['DROP', 'SELECT', 'DELETE' 'UPDATE', 'INSERT', 'EXEC', '--', '/*', '*/', 'xp_', 'sp_']

    @classmethod
    def print(cls, msg):
        if cls.print_msg:
            print(f"\033[92m{msg}\033[0m")

    @classmethod
    def get_params_without_paginated(cls, params: typing.Dict):
        if not params:
            return {}
        params_cp = copy.deepcopy(params)
        if cls.page_param in params:
            del params_cp[cls.page_param]
        if cls.page_size_param in params:
            del params_cp[cls.page_size_param]
        return params_cp

    @classmethod
    def set_where_phrase(cls, sql, where):
        """
        生成where语句
        """
        if not where:
            return sql
        where_str = " WHERE "
        for key in where.keys():
            where_str += key + " = :" + "_where_%s" % key + " and "
        where_str = where_str[0:-5]
        sql += where_str
        return sql

    @classmethod
    def fullfilled_data(cls, data, where):
        """
        删除/更新操作,对传入的data 在where条件中的字段都新增一个 _where_${field} 字段,用于where条件的赋值
        """
        if not where:
            return data

        for k, v in where.items():
            if k.startswith("_where_"):
                raise Exception("where条件中不能包含 _where_ 开头的字段")
            data.update(**{
                "_where_%s" % k: v
            })

        return data

    @classmethod
    def dictfetchall(cls, cursor, is_obj=True):
        "Return all rows from a cursor as a dict"
        columns = [col[0] for col in cursor.description]
        if is_obj:
            return [
                DBData(zip(columns, row))
                for row in cursor.fetchall()
            ]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]


    @classmethod
    def filter_sql_injection(cls, input_string):
        for keyword in cls.sql_injection_keywords:
            if keyword in input_string.upper():
                raise ValueError('Keywords that may be at risk for SQL injection:' + keyword)
        return input_string

    @classmethod
    def set_exclude_phrase(cls, sql, exclude):
        """
        Generate exclude statement
        """
        if not exclude:
            return sql

        if "WHERE" not in sql.upper():
            sql += " WHERE "
        else:
            sql += " AND "

        for key, val in exclude.items():
            sql += cls.handle_ops(key, val, opt_type="exclude")
        sql = sql[0:-5]

        return sql

    @classmethod
    def handle_ops(cls, key, val, opt_type="where"):
        """
        包括的操作符包括: __in、__gt、__gte、__lt、__lte、__like、__isnull、__between
        Handle more types of operations.
        key: key for either "where" or "exclude"
        val: value for either "where" or "exclude"
        opt_type: "where" or "exclude"
        """
        filter_str = '_where_' if opt_type == 'where' else '_exclude_'
        operator_mapping = {
            '__gt': '>=',
            '__gte': '>=',
            '__lt': '<',
            '__lte': '<=',
            '__like': 'LIKE',
            '__in': 'IN',
            '__isnull': 'IS NULL' if val else 'IS NOT NULL',
            '__between': 'BETWEEN'
        }
        exclude_mapping = {
            '__gt': '<',
            '__gte': '<',
            '__lt': '>=',
            '__lte': '>',
            '__like': 'NOT LIKE',
            '__in': 'NOT IN',
            '__isnull': 'IS NOT NULL' if val else 'IS NULL',
            '__between': 'NOT BETWEEN'
        }

        for op, sql_op in operator_mapping.items():
            if key.endswith(op):
                if opt_type == 'exclude':
                    sql_op = exclude_mapping[op]
                _key = key.replace(op, '')
                if op == '__between':
                    phrase = f"{_key} {sql_op} :{filter_str}_between_1_{key} AND :{filter_str}_between_2_{key} AND "
                elif op == '__isnull':
                    phrase = f"{_key} {sql_op} AND "
                else:
                    phrase = f"{_key} {sql_op} :{filter_str}{key} AND "
                return phrase

        return f"{key} = :_where_{key} AND"

    @classmethod
    def execute_update(cls, tb_name, data, where):
        """
        更新数据
        """
        tb_name = cls.filter_sql_injection(tb_name)
        sql = "UPDATE " + tb_name + " SET "
        for key in data.keys():
            sql += "`%s`" % key + " = :" + key + ","
        sql = sql[0:-1]

        data = cls.fullfilled_data(data, where)
        sql = cls.set_where_phrase(sql, where)
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, data)
                return cursor.rowcount
        except Exception as e:
            cls.print("Failed to execute sql: < %s %s >! Cause: %s" % (sql, str(data), str(e)))
            return None

    @classmethod
    def execute_create(cls, tb_name, data):
        """
        插入数据
        """
        tb_name = cls.filter_sql_injection(tb_name)
        sql = "INSERT INTO " + tb_name + " ("
        for key in data.keys():
            sql += "`%s`" % key + ","
        sql = sql[0:-1]
        sql += ") VALUES ("
        for key in data.keys():
            sql += ":" + key + ","
        sql = sql[0:-1]
        sql += ")"
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, data)
                return cursor.lastrowid
        except Exception as e:
            cls.print("Failed to execute sql: < %s %s >! Cause: %s" % (sql, str(data), str(e)))
            return None

    @classmethod
    def execute_delete(cls, tb_name, where, logic=False, exclude=None):
        """
        删除数据
        """
        tb_name = cls.filter_sql_injection(tb_name)
        sql = "DELETE FROM " + tb_name
        if logic:
            sql = "UPDATE %s SET is_delete=1" % tb_name
        sql = cls.set_where_phrase(sql, where)
        sql = cls.set_exclude_phrase(sql, exclude)
        where = cls.fullfilled_data({}, where)

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, where)
                return cursor.rowcount
        except Exception as e:
            cls.print("Failed to execute sql: < %s %s >! Cause: %s" % (sql, str(where), str(e)))
            return None

    @classmethod
    def execute_sql(cls, sql_id, params=None, options: typing.Dict[str, any] = None, return_obj=True):
        """
        动态sql通用方法
        """
        preloaded_sql = sql_loader.preload_sql(sql_id, options=options)
        try:
            with connection.cursor() as cursor:
                cursor.execute(preloaded_sql, params)
                cls.print("Current sql execution: %s %s" % (preloaded_sql, str(params)))
                return cls.dictfetchall(cursor, is_obj=return_obj)
        except Exception as e:
            cls.print("Failed to execute sql: %s %s! Cause :%s" % (preloaded_sql, str(params), str(e)))

        return []

    @classmethod
    def select_one(cls, sql_id, params=None, options: typing.Dict[str, str] = None, return_obj=True):
        options = cls.get_params_without_paginated(options)  # 不需要分页
        result = cls.execute_sql(sql_id, params, options, return_obj=return_obj)
        return result[0] if result else {}

    @classmethod
    def select_all(cls, sql_id, params=None, options: typing.Dict[str, typing.Union[str, int, None]] = None, return_obj=True):
        return cls.execute_sql(sql_id, params, options, return_obj=return_obj)
