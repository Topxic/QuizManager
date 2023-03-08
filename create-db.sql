CREATE TABLE IF NOT EXISTS quiz (
    quiz_id BINARY(16) PRIMARY KEY,
    message_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    creator_id BIGINT NOT NULL,
    question TEXT NOT NULL,
    time_to_live INTEGER NOT NULL,
    closed BOOLEAN NOT NULL,
    UNIQUE KEY (message_id, channel_id, creator_id)
);

CREATE INDEX time_to_live
ON quiz (time_to_live);

CREATE INDEX closed
ON quiz (closed);

CREATE TABLE IF NOT EXISTS answer (
    answer_id BINARY(16) PRIMARY KEY,
    quiz_id BINARY(16) NOT NULL,
    answer TEXT NOT NULL,
    correct BOOLEAN NOT NULL,
    FOREIGN KEY(quiz_id) REFERENCES quiz(quiz_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS given_answer (
    quiz_id BINARY(16) NOT NULL,
    answer_id BINARY(16) NOT NULL,
    player_id BIGINT NOT NULL,
    PRIMARY KEY (quiz_id, answer_id, player_id),
    FOREIGN KEY(quiz_id) REFERENCES quiz(quiz_id) ON DELETE CASCADE,
    FOREIGN KEY(answer_id) REFERENCES answer(answer_id) ON DELETE CASCADE
)
