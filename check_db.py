import asyncio
import asyncpg
import os

DATABASE_URL = "postgresql://neondb_owner:npg_2oxH1RDbWJCK@ep-spring-bird-axqxrk06-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require"

async def main():
    conn = await asyncpg.connect(DATABASE_URL)
    tables = await conn.fetch("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
    print("Tables:", [t['tablename'] for t in tables])
    
    # check site_articles schema
    try:
        columns = await conn.fetch("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'site_articles';")
        print("site_articles columns:", [dict(c) for c in columns])
    except Exception as e:
        print(e)
        
    await conn.close()

asyncio.run(main())
