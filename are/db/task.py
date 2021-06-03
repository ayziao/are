from are.db import get_db


def get_one(number):
    row = get_db().execute(
        'SELECT * '
        ' FROM task'
        ' WHERE 連番 = ?',
        (number,)
    ).fetchone()

    return row


def get_list(args):
    where = ' WHERE "状態" <> "特殊な状態"'

    if args['status']:
        where += ' AND "状態" = "' + args['status'] + '" '
    if args['owner']:
        if args['owner'][0] == '-':
            where += ' AND "所有者" <> "' + args['owner'][1:] + '" '
        else:
            where += ' AND "所有者" = "' + args['owner'] + '" '
    if args['rate']:
        if 'only' in args['rate']:
            where += ' AND "重要度" = "' + args['rate'][0] + '" '
        elif 'over' in args['rate']:
            where += ' AND "重要度" >= "' + args['rate'][0] + '" '
        else:
            where += ' AND "重要度" <= "' + args['rate'] + '"  AND "重要度" <> 0 '
    if args['cost']:
        where += ' AND "コスト" = "' + args['cost'] + '" '
    if args['tag']:
        if args['tag'][0] == '-':
            where += ' AND "タグ" NOT LIKE "% ' + args['tag'][1:] + ' %" '
        else:
            where += ' AND "タグ" LIKE "% ' + args['tag'] + ' %" '
    if args['tag1st']:
        if args['tag1st'][0] == '-':
            where += ' AND "タグ" NOT LIKE " ' + args['tag1st'][1:] + ' %" '
        else:
            where += ' AND "タグ" LIKE " ' + args['tag1st'] + ' %" '
    if 'notag' in args:
        where += ' AND ("タグ" = "" OR "タグ" = "  ") '
    if args['cycle']:
        if args['cycle'] == "routine":
            where += ' AND ("タグ" LIKE "% 年 %" OR "タグ" LIKE "% 月 %" OR "タグ" LIKE "% 週 %" OR ' \
                     ' "タグ" LIKE "% 日 %" OR "タグ" LIKE "% 寝 %" OR "タグ" LIKE "% 食 %")'
        elif args['cycle'] == "randomly":
            where += ' AND ("タグ" LIKE "% 繰り返し %" OR "タグ" LIKE "% 常備 %") '
        else:
            where += ' AND "タグ" NOT LIKE "% 年 %" AND "タグ" NOT LIKE "% 月 %" AND "タグ" NOT LIKE "% 週 %" ' \
                     ' AND "タグ" NOT LIKE "% 日 %" AND "タグ" NOT LIKE "% 寝 %" AND "タグ" NOT LIKE "% 食 %" ' \
                     ' AND "タグ" NOT LIKE "% 常備 %" AND "タグ" NOT LIKE "% 繰り返し %" '
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

    # print(sql)

    rows = get_db().execute(sql).fetchall()
    return rows
