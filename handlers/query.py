from sqlalchemy import and_, func, select

from db.schema import all_tokens

CHECK_TOKEN = select([all_tokens.c.token])
