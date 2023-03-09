CREATE TABLE IF NOT EXISTS quiz (
    quiz_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    message_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    creator_id BIGINT NOT NULL,
    question TEXT NOT NULL,
    time_to_live INTEGER NOT NULL,
    finished BOOLEAN DEFAULT 1,
    UNIQUE KEY (message_id, channel_id, creator_id)
);

CREATE INDEX creator_id
ON quiz (creator_id);

CREATE INDEX time_to_live
ON quiz (time_to_live);

CREATE INDEX finished
ON quiz (finished);

CREATE INDEX time_to_live_finished
ON quiz (time_to_live, finished);


CREATE TABLE IF NOT EXISTS answer (
    answer_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    quiz_id INT UNSIGNED NOT NULL,
    emoji CHAR NOT NULL,
    answer TEXT NOT NULL,
    correct BOOLEAN NOT NULL,
    UNIQUE KEY (quiz_id, emoji, answer)
    FOREIGN KEY(quiz_id) REFERENCES quiz(quiz_id) ON DELETE CASCADE
);

CREATE INDEX quiz_id
ON answer (quiz_id);

CREATE TABLE IF NOT EXISTS given_answer (
    quiz_id INT UNSIGNED NOT NULL,
    answer_id INT UNSIGNED NOT NULL,
    player_id BIGINT NOT NULL,
    PRIMARY KEY (quiz_id, answer_id, player_id),
    FOREIGN KEY(quiz_id) REFERENCES quiz(quiz_id) ON DELETE CASCADE,
    FOREIGN KEY(answer_id) REFERENCES answer(answer_id) ON DELETE CASCADE
)
