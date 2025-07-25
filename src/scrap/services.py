from sqlalchemy import Select

from src.scrap.schemas import PostSchema

from src.scrap.models import Post

async def get_all_post(max_post, db) -> list[PostSchema] | Exception:
    try:
        query = Select(Post).limit(max_post)

        res = await db.execute(query)
        
        list_post = list(res.scalars().all())

        validated_posts = [
            PostSchema.model_validate(post, from_attributes=True)
            for post in list_post
        ]

        return validated_posts   

    except Exception as e:
        return e
