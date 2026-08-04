import { neon } from "@neondatabase/serverless";
import dotenv from "dotenv";

dotenv.config({ path: "./.env.local" });

async function run() {
  const sql = neon(process.env.DATABASE_URL);
  
  console.log("Dropping conflicting articles table...");
  try {
    await sql.query("DROP TABLE articles CASCADE;");
  } catch(e) {}
  
  console.log("Done.");
}

run().catch(console.error);
