-- Enable Foreign Keys
PRAGMA foreign_keys = ON;

-- Table: items
-- Stores the unique jade pendants identified by their item code.
CREATE TABLE IF NOT EXISTS items (
    item_code TEXT PRIMARY KEY,
    title TEXT,
    description_hero TEXT,
    description_modern TEXT, -- E-commerce style description
    description_social TEXT, -- Social media style description
    attributes_json TEXT, -- Stores JSON object of features (Color, Motif, etc.)
    rarity_rank TEXT DEFAULT 'B', -- Rarity Tier (S, A, B)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table: images
-- Stores the source image files scanned by the system.
CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT UNIQUE NOT NULL,
    processed_status TEXT DEFAULT 'PENDING', -- PENDING, PROCESSED, ERROR
    scan_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table: item_images
-- Junction table linking items to images (Many-to-Many, as one image has many items, 
-- and one item might appear in multiple images).
CREATE TABLE IF NOT EXISTS item_images (
    item_code TEXT NOT NULL,
    image_id INTEGER NOT NULL,
    is_primary BOOLEAN DEFAULT 0,
    FOREIGN KEY (item_code) REFERENCES items(item_code) ON DELETE CASCADE,
    FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE,
    PRIMARY KEY (item_code, image_id)
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_items_code ON items(item_code);
CREATE INDEX IF NOT EXISTS idx_images_path ON images(file_path);

-- Table: telemetry
-- Stores execution logs for debugging and performance tracking.
CREATE TABLE IF NOT EXISTS telemetry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    program TEXT,
    version TEXT,
    command TEXT,
    module TEXT,
    action TEXT,
    args TEXT, -- Stored as JSON string
    user TEXT,
    host TEXT,
    os TEXT,
    runtime TEXT,
    duration_ms REAL,
    cpu_time_ms REAL,
    gpu_time_ms REAL,
    memory_mb REAL,
    exit_code INTEGER,
    error TEXT,
    context_json TEXT, -- cwd, env, tags stored as JSON
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON telemetry(timestamp);
CREATE INDEX IF NOT EXISTS idx_telemetry_module ON telemetry(module);
