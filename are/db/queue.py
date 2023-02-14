def create(db, type_, content):
    db.execute(
        'INSERT INTO queue (reservation_time, queue_type, content, add_time)'
        ' VALUES (CURRENT_TIMESTAMP, ?, ?, CURRENT_TIMESTAMP)',
        (type_, content)
    )
