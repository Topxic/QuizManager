CREATE TABLE IF NOT EXISTS quiz (
    quiz_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    message_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    creator_id BIGINT NOT NULL,
    question TEXT NOT NULL,
    time_to_live INTEGER NOT NULL,
    finished BOOLEAN DEFAULT 1,
    UNIQUE (message_id, channel_id, creator_id)
);

CREATE TABLE IF NOT EXISTS answer (
    answer_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    quiz_id INT UNSIGNED NOT NULL,
    emoji CHAR NOT NULL,
    answer TEXT NOT NULL,
    correct BOOLEAN NOT NULL,
    UNIQUE (quiz_id, emoji),
    FOREIGN KEY(quiz_id) REFERENCES quiz(quiz_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS given_answer (
    quiz_id INT UNSIGNED NOT NULL,
    answer_id INT UNSIGNED NOT NULL,
    player_id BIGINT NOT NULL,
    PRIMARY KEY (quiz_id, player_id),
    FOREIGN KEY(quiz_id) REFERENCES quiz(quiz_id) ON DELETE CASCADE,
    FOREIGN KEY(answer_id) REFERENCES answer(answer_id) ON DELETE CASCADE
);

-- Used to update/finish all unfinished quizzes
CREATE INDEX time_to_live_finished
ON quiz (time_to_live, finished);

-- Used to get all answers for a specific quiz
CREATE INDEX quiz_id
ON answer (quiz_id);

-- Used for grouping by player_id
CREATE INDEX player_id
ON given_answer (player_id);

-- Improve performance of correct answer lookup
CREATE INDEX correct
ON answer (correct);

-- Speedup join with quiz table
CREATE INDEX given_answer_quiz_id
ON given_answer (quiz_id);

-- Used to count number of quizzes per channel
CREATE INDEX channel_id
ON quiz (channel_id);
