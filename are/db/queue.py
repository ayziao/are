def create(db, type, content):
    db.execute(
        'INSERT INTO queue (reservation_time, queue_type, content, add_time)'
        ' VALUES (CURRENT_TIMESTAMP, ?, ?, CURRENT_TIMESTAMP)',
        (type, content)
    )
