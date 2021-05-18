from are.db import get_db


def get_list(args):
    where = ' WHERE "状態" <> "特殊な状態"'
    if args['owner']:
        if args['owner'][0] == '-':
            where += ' AND "所有者" <> "' + args['owner'][1:] + '" '
        else:
            where += ' AND "所有者" = "' + args['owner'] + '" '
    if args['rate']:
        if 'only' in args['rate']:
            where += ' AND "重要度" = "' + args['rate'][0] + '" '
        else:
            where += ' AND "重要度" <= "' + args['rate'] + '"  AND "重要度" <> 0'
    if args['cost']:
        where += ' AND "コスト" = "' + args['cost'] + '" '
    if args['tag']:
        if args['tag'][0] == '-':
            where += ' AND "タグ" NOT LIKE "% ' + args['tag'][1:] + ' %" '
        else:
            where += ' AND "タグ" LIKE "% ' + args['tag'] + ' %" '
    if args['cycle']:
        if args['cycle'] == "routine":
            where += ' AND ("所有者" = "年" OR "所有者" = "月" OR "所有者" = "週" OR "所有者" = "日" ' \
                     ' OR "所有者" = "寝" OR "所有者" = "食")'
        elif args['cycle'] == "randomly":
            where += ' AND ("タグ" LIKE "%繰り返し%" OR "タグ" LIKE "%常備%") '
        else:
            where += ' AND "所有者" <> "年" AND "所有者" <> "月" AND "所有者" <> "週" AND "所有者" <> "日" ' \
                     ' AND "所有者" <> "寝" AND "所有者" <> "食" ' \
                     ' AND "タグ" NOT LIKE "%常備%" AND "タグ" NOT LIKE "%繰り返し%" '
    if args['title']:
        where += ' AND "タスク名" LIKE "%' + args['title'] + '%" '

    order = ' ORDER BY "状態" DESC, "完了日時" DESC, ' \
            ' CASE "重要度" WHEN 0 THEN 9 ELSE "重要度" END DESC, ' \
            ' "変更日時" DESC '
    if args['sort'] == 'time':
        order = ' ORDER BY "状態" DESC, "完了日時" DESC, "連番" DESC '
    if args['sort'] == 'update':
        order = ' ORDER BY "状態" DESC, "完了日時" DESC, "変更日時" DESC '
    if args['sort'] == 'cost':
        order = ' ORDER BY "状態" DESC, "完了日時" DESC, "コスト" '
    if args['sort'] == 'title':
        order = ' ORDER BY "状態" DESC, "タスク名" '

    sql = 'SELECT *, ' \
          ' strftime("%Y-%m-%d ", "完了日時") || ' \
          '     substr("0"||(strftime("%H", "完了日時")+9),-2,2) || ' \
          '     strftime(":%M:%S", "完了日時") as utcP9time ' \
          ' FROM task ' + where + order
    rows = get_db().execute(sql).fetchall()
    return rows
