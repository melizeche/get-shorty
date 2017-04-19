create table urls (
      id integer primary key autoincrement,
      short text unique not null,
      default_url text not null,
      default_hits integer default 0,
      mobile_url text,
      mobile_hits integer default 0,
      tablet_url text,
      tablet_hits integer default 0,
      created datetime default current_timestamp
        );