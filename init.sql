CREATE SCHEMA gfs;

CREATE TABLE IF NOT EXISTS gfs.files (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(256),
    chunks   INT,
    filesize INT
);

CREATE TABLE IF NOT EXISTS gfs.chunks (
    chunk_handler VARCHAR(256) PRIMARY KEY,
    fileid INT,
    chunk_pos INT,

    CONSTRAINT fk_file
        FOREIGN KEY (fileid)
        REFERENCES gfs.files(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS gfs.chunks_map (
    id SERIAL PRIMARY KEY,
    chunk_handler VARCHAR(256),
    server_name VARCHAR(150),

    CONSTRAINT fk_chunks
        FOREIGN KEY (chunk_handler)
        REFERENCES gfs.chunks(chunk_handler)
        ON DELETE CASCADE
);
