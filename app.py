from flask import Flask, render_template, request
import json

app = Flask("Emma")

@app.route("/")
def index():
    return render_template("mysql.html")

@app.route("/mysql/sql")
def mysql_sql():
    schema = json.loads(request.args.get("schema"))
    db = schema["db"]
    if db == "":
        return json.dumps({"error": "库名不可为空"})
    table = schema["table"]
    if table == "":
        return json.dumps({"error": "表名不可为空"})
    table_comment = schema["comment"]
    if table_comment == "":
        return json.dumps({"error": "表注释不可为空"})
    primary_keys = []
    sql = f"DROP TABLE IF EXISTS `{db}`.`{table}`;\n"
    sql = sql + f"CREATE TABLE `{db}`.`{table}`(\n"
    if len(schema["cols"]) == 0:
        return json.dumps({"error": "需要至少有一列"})
    for col in schema["cols"]:
        name = col["name"]
        if name == "":
            return json.dumps({"error": "列名不可为空"})
        type = col["type"]
        if type == "":
            return json.dumps({"error": f"列{name}的类型不可为空"})
        if type == "varchar":
            try:
                varchar_len = int(col["varchar_len"])
            except:
                return json.dumps({"error": f"列{name}的类型为varchar，长度应该是个数字"})
            type = f"varchar({varchar_len})"
        primary = col["primary"]
        nullable = col["nullable"]
        default = col["default"]
        if type == "varchar":
            default = f"'{default}'"
        elif type == "int":
            try:
                default = int(default)
            except:
                return json.dumps({"error": f"列{name}的类型为int，默认值应该是个int"})
        elif type == "float":
            try:
                default = float(default)
            except:
                return json.dumps({"error": f"列{name}的类型为float，默认值应该是个float"})
        elif type == "date":
            default = f"'{default}'"
        else:
            return json.dumps({"error": f"列{name}未知类型{type}"})
        comment = col["comment"]
        if comment == "":
            return json.dumps({"error": f"列{name}的注释不可为空"})
        col_sql = f"    `{name}` {type}"
        if not nullable:
            col_sql = col_sql + " NOT NULL"
        col_sql = col_sql + f" DEFAULT {default} COMMENT '{comment}',\n"
        sql = sql + col_sql
        if primary:
            if nullable:
                return json.dumps({"error": f"列{name}是主键不可为空"})
            primary_keys.append(f"`{name}`")
    if len(primary_keys) == 0:
        return json.dumps({"error": "没有设置主键"})
    sql = sql + f"    primary key({','.join(primary_keys)})"
    sql = sql + f"\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='{table_comment}';"
    return json.dumps({"sql": sql})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5140)