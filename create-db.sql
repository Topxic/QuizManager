CREATE TABLE IF NOT EXISTS quiz (
    message_id BIGINT PRIMARY KEY,
    channel_id BIGINT NOT NULL,
    creator_id BIGINT NOT NULL,
    question TEXT NOT NULL,
    time_to_live INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS answer (
    message_id BIGINT,
    answer TEXT,
    correct BOOLEAN,
    FOREIGN KEY(message_id) REFERENCES quiz(message_id)
)
