""" this is just a file to house the displays db structure"""

# displays & dashboards section
# for integer columns variable input enter 0
# for text column variable input enter var
display_types = """ CREATE TABLE IF NOT EXISTS display_types (
                                dt_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                x_min TEXT,
                                x_resolution INTEGER,
                                x_resolution_unit TEXT,
                                x_max TEXT,
                                x_window_size INTEGER,
                                x_window_unit TEXT,
                                x_source_col TEXT NOT NULL,
                                graph_type TEXT NOT NULL,
                                proj_type TEXT,
                                proj_resolution INTEGER NOT NULL,
                                proj_resolution_unit TEXT
        
                            ); """

dashboards = """ CREATE TABLE IF NOT EXISTS dashboards (
                                dash_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                dash_desc TEXT NOT NULL,
                                dash_date DATETIME DEFAULT CURRENT_TIMESTAMP
        
                            ); """

# display types and link tables
cm_records = """ CREATE TABLE IF NOT EXISTS cm_records (
                                cm_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                cm_target REAL NOT NULL,
                                cm_resolution,
                                cm_type TEXT NOT NULL CHECK(cm_type IN ('budget','goal','account')),
                                cm_desc TEXT,
                                g_profile INTEGER,
                                acc_date DATETIME
                                
                            ); """


cm_sources = """ CREATE TABLE IF NOT EXISTS cm_sources (
                                cm_id INTEGER NOT NULL,
                                source_table TEXT NOT NULL,
                                source_w_col TEXT NOT NULL,
                                source_y_col TEXT NOT NULL,
                                source_cond TEXT CHECK(source_cond IN ('=', 'LIKE', '<=', '>=')),
                                source_id INTEGER,
                                created DATETIME DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY (cm_id) REFERENCES cm_records (cm_id) ON DELETE CASCADE ON UPDATE CASCADE
                                
                            ); """

displays_dashboards = """ CREATE TABLE IF NOT EXISTS cm_dashboards (
                                cm_id INTEGER,
                                dt_id INTEGER,
                                dash_id INTEGER,
                                FOREIGN KEY (dt_id) REFERENCES display_types (dt_id) ON DELETE CASCADE ON UPDATE CASCADE,
                                FOREIGN KEY (cm_id) REFERENCES cm_records (cm_id) ON DELETE CASCADE ON UPDATE CASCADE,
                                FOREIGN KEY (dash_id) REFERENCES dashboards (dash_id) ON DELETE CASCADE ON UPDATE CASCADE
        
                            ); """

DISPLAY_TABLES = [display_types, dashboards, displays_dashboards, cm_records, cm_sources]
