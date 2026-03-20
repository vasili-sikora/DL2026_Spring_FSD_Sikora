CREATE TABLE IF NOT EXISTS templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    image_path TEXT NOT NULL,
    top_text_x INTEGER,
    top_text_y INTEGER,
    top_text_width INTEGER,
    bottom_text_x INTEGER,
    bottom_text_y INTEGER,
    bottom_text_width INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS generated_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    text_top TEXT,
    text_bottom TEXT,
    image_path TEXT NOT NULL,
    share_token TEXT UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES templates(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS ind_generated_images_user_id ON generated_images(user_id);
