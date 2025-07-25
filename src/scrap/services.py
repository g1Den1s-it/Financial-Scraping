import logging
from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError

from src.scrap.schemas import PostSchema

from src.scrap.models import Post


logger = logging.getLogger(__name__)


async def get_all_post(db) -> list[PostSchema] | Exception:
    try:
        query = Select(Post)

        res = await db.execute(query)
        
        list_post = list(res.scalars().all())

        validated_posts = [
            PostSchema.model_validate(post, from_attributes=True)
            for post in list_post
        ]
        logger.info("Fetched data from database successful")
        return validated_posts   
    except Exception as e:
        logger.error("Can not fetched data from database: " + str(e))
        return e


def get_all_post_query():
    return select(Post)


async def create_post(data: PostSchema ,db):
    try:
        post = Post(
            url=data.url,
            title=data.title,
            content=data.content,
            author=data.author,
            published_at=data.published_at,
            scraped_at=data.scraped_at
        )

        db.add(post)
        await db.commit()

        logger.info("Saved data in database successful")
        return data
    except IntegrityError as e:
        logger.error("Can not save data in database due to unique constraint violation.")
        await db.rollback()
    except Exception as e:
        logger.error("Can not save data in database: " + str(e))
        return e
        