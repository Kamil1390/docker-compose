-- Создание таблицы для фьючерсов
DROP TABLE IF EXISTS Futures CASCADE;
CREATE TABLE Futures (
    Symbol VARCHAR PRIMARY KEY,
    Name VARCHAR UNIQUE NOT NULL,
    Country VARCHAR(10),
    Sector VARCHAR,
    Exchange VARCHAR
);

-- Создание таблицы для данных о фючерсах по месяцам
DROP TABLE IF EXISTS InstrumentDetails CASCADE;
CREATE TABLE InstrumentDetails (
    ID SERIAL PRIMARY KEY,
    Symbol VARCHAR,
    DateTrade VARCHAR(7),
    DateExpiration Date,
    ContractSize INT,
    InitMargin DECIMAL(10, 2),
    FOREIGN KEY(Symbol) REFERENCES Futures(Symbol)
);

-- Создание таблицы для дневных данных за несколько лет
DROP TABLE IF EXISTS DailyData CASCADE;
CREATE TABLE DailyData (
    DailyID SERIAL PRIMARY KEY,
    Symbol VARCHAR,
    DayTrade DATE,
    OpenPrice DECIMAL(10, 2),
    HighPrice DECIMAL(10, 2),
    LowPrice DECIMAL(10, 2),
    ClosePrice DECIMAL(10, 2),
    Volume INT,
    Annotation TEXT,
    FOREIGN KEY(Symbol) REFERENCES Futures(Symbol)
);

-- Добавление новой колонки для всех таблиц
alter table Futures add update_at TIMESTAMP(0);
alter table InstrumentDetails add update_at TIMESTAMP(0);
alter table DailyData add update_at TIMESTAMP(0);

-- Создание триггерной функции для insert_update
CREATE OR REPLACE FUNCTION insert_update()
    RETURNS trigger AS $$
BEGIN
    NEW.update_at = now();
    RETURN NEW;
END;
$$LANGUAGE plpgsql;

-- Создание триггерной функции для annotation
CREATE OR REPLACE FUNCTION insert_annotation()
    RETURNS trigger AS $$
BEGIN
    NEW.annotation = upper(md5(random()::text));
    RETURN NEW;
END;
$$LANGUAGE plpgsql;

-- Создание триггера заполняющего поле UPDATE_AT для всех таблиц
CREATE TRIGGER insert_update_trigger
BEFORE INSERT OR UPDATE ON futures
FOR EACH ROW
EXECUTE FUNCTION insert_update();

CREATE TRIGGER insert_update_trigger
BEFORE INSERT OR UPDATE ON instrumentdetails
FOR EACH ROW
EXECUTE FUNCTION insert_update();

CREATE TRIGGER insert_update_trigger
BEFORE INSERT OR UPDATE ON dailydata
FOR EACH ROW
EXECUTE FUNCTION insert_update();

-- Создание триггера заполняющего поле ANNOTATION для DailyData
CREATE TRIGGER insert_annotation_trigger
BEFORE INSERT OR UPDATE ON dailydata
FOR EACH ROW
EXECUTE FUNCTION insert_annotation();

-- Заполнение таблицы фьючерсов
COPY Futures(Symbol,Name,Country,Sector,Exchange) FROM '/docker-entrypoint-initdb.d/fut_tabl.csv' DELIMITER ',' CSV HEADER;
-- Заполнение таблицы инструмент детаилс
COPY InstrumentDetails(Symbol, DateTrade, DateExpiration, ContractSize, InitMargin) FROM '/docker-entrypoint-initdb.d/details_tabl.csv' DELIMITER ',' CSV HEADER;
-- Заполнение таблицы дневной торговли
COPY DailyData(Symbol, DayTrade, OpenPrice, HighPrice, LowPrice, ClosePrice, Volume) FROM '/docker-entrypoint-initdb.d/daily_tabl.csv' DELIMITER ',' CSV HEADER;

-- Создание индексов
CREATE INDEX ind_volume ON dailydata(daytrade);
CREATE INDEX ind_open_price ON dailydata(openprice);
CREATE INDEX ind_init_margin ON instrumentdetails(initmargin);