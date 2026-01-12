import * as duckdb from "npm:@duckdb/duckdb-wasm";

const PARQUET_URL =
  "https://kansenshou.ringsaturn.me/data/teiten/merged_teiten.parquet";

const db = await duckdb.createDB();
const conn = await db.connect();

const result = await conn.query(`
  SELECT * FROM read_parquet('${PARQUET_URL}')
`);

process.stdout.write(JSON.stringify(result.toArray()));
