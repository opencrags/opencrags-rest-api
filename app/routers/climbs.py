from uuid import UUID

from app import create_api_router, VoteDefinition


router = create_api_router(
    model_name="Climbs",
    collection_name="climbs",
    item_name="climb",
    statics=dict(
        crag_id=UUID,
        sector_id=UUID,
    ),
    voted=[
        VoteDefinition(
            model_name="ClimbNameVote",
            collection_name="name_votes",
            item_name="name_vote",
            type=str,
        ),
        VoteDefinition(
            model_name="RatingVote",
            collection_name="rating_votes",
            item_name="rating_vote",
            type=int,
        ),
        VoteDefinition(
            model_name="GradeVote",
            collection_name="grade_votes",
            item_name="grade_vote",
            type=UUID,
        ),
        VoteDefinition(
            model_name="ClimbTypeVote",
            collection_name="climb_type_votes",
            item_name="climb_type_vote",
            type=str,  # TODO enum: sport, boulder, partially bolted, trad, alpine
        ),
        VoteDefinition(
            model_name="SitStartVote",
            collection_name="sit_start_votes",
            item_name="sit_start_vote",
            type=str,
        ),
        VoteDefinition(
            model_name="DefinedStartVote",
            collection_name="defined_start_votes",
            item_name="defined_start_vote",
            type=str,
        ),
        VoteDefinition(
            model_name="EliminationsVote",
            collection_name="eliminations_votes",
            item_name="eliminations_vote",
            type=str,  # TODO: draw area of eliminations?
        ),
        VoteDefinition(
            model_name="DescriptionVote",
            collection_name="description_votes",
            item_name="description_vote",
            type=str,
        ),
        # guide book grade?
        # first ascent grade?
        # point to other page with information?
        # point to video + timestamp with beta
    ]
)
