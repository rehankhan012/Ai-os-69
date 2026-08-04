import { neon } from "@neondatabase/serverless";
import fs from "fs";
import dotenv from "dotenv";

dotenv.config({ path: "../.env.local" });

async function run() {
  const sql = neon(process.env.DATABASE_URL);
  const schema = fs.readFileSync("./schema.sql", "utf-8");
  const queries = schema.split(";").filter(q => q.trim() !== "");
  
  console.log("Applying schema...");
  for (const q of queries) {
    if (q.trim()) {
      await sql.query(q);
    }
  }
  console.log("Schema applied successfully.");
}

run().catch(console.error);
