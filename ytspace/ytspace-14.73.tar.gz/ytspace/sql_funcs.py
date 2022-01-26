import mysql.connector as mysql;

def connect_to_mysql(host = "localhost", port = 3306):
    user = input("Enter the MySQL username: ")
    passwd = input(f"Enter the password for {user}: ")

    try:
        main_connection = mysql.connect (
            host = host,
            port = port,
            user = user,
            passwd = passwd,
            charset = "utf8",
            auth_plugin = "mysql_native_password"
        )
        return main_connection

    except mysql.errors.ProgrammingError:
        print("Incorrect username or password, please try again.")
        return connect_to_mysql()
    except mysql.errors.NotSupportedError:
    	print("Invalid username or password, please try again.")

def cursor_connection(connection):
    if connection.is_connected():
        print("\nConnected to the local MySQL server successfully.\n")
    else:
        print("Failed to connect to the server. Try again.")
        return

    return connection.cursor()

################ MySQL Queries ################

add_media = ("INSERT INTO media"
             "(type, source_link, date, time)"
             "VALUES (%s,%s,%s,%s)")

add_video_music = ("INSERT INTO {} "
                   "(media_id, title, size_mb, file_name) "
                   "VALUES (%s,%s,%s,%s)")

delete_media = ("DELETE FROM media WHERE id = {}")

delete_video_music = ("DELETE FROM {} WHERE media_id = {}")

find_type = ("SELECT type FROM media WHERE id = {}")

display_video_music = ("""
			SELECT
				m.id, vm.title, t.path, m.date, m.time
			FROM media m
			JOIN type t ON t.type      = m.type
			JOIN {} vm  ON vm.media_id = m.id
			WHERE m.id = {}""")

display_all_video_music = ("""
			SELECT
				m.id, vm.title, t.path, m.date, m.time
			FROM media m
			JOIN type t ON t.type	   = m.type
			JOIN {} vm  ON vm.media_id = m.id
			""")

update_title = ("""
            UPDATE {}
            SET title = "{}"
            WHERE media_id = {}
            """)

################ DATABASE SCHEMA ################

table_type = ("""
            CREATE TABLE IF NOT EXISTS type (
                type INT NOT NULL,
                extension VARCHAR(7) NOT NULL,
                path VARCHAR(511) NOT NULL,
                PRIMARY KEY (type)
            )
            """)

table_media = ("""
            CREATE TABLE IF NOT EXISTS media (
                id INT UNSIGNED AUTO_INCREMENT,
                type INT NOT NULL,
                source_link VARCHAR(255) NOT NULL,
                date DATE NOT NULL,
                time TIME NOT NULL,
                PRIMARY KEY (id),
                FOREIGN KEY (type) REFERENCES type(type)
            )
            """)

table_videos = ("""
            CREATE TABLE IF NOT EXISTS videos (
                media_id INT UNSIGNED,
                title VARCHAR(511) NOT NULL,
                size_mb DECIMAL(8,2) NOT NULL,
                file_name VARCHAR(511) NOT NULL,
                PRIMARY KEY (media_id),
                FOREIGN KEY (media_id) REFERENCES media(id)
            )
            """)

table_music = ("""
            CREATE TABLE IF NOT EXISTS music (
                media_id INT UNSIGNED,
                title VARCHAR(511) NOT NULL,
                size_mb DECIMAL(8,2) NOT NULL,
                file_name VARCHAR(511) NOT NULL,
                PRIMARY KEY (media_id),
                FOREIGN KEY (media_id) REFERENCES media(id)
            )
            """)

type_init = ("""
            INSERT IGNORE INTO type 
            VALUES  (0, '.mp3', '{}'),
                    (1, '.mp4', '{}')
            """)
