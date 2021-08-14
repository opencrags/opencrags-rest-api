from uuid import UUID

from app import create_api_router, VoteDefinition


router, MainModel, vote_models = create_api_router(
    model_name="Crag",
    collection_name="crags",
    item_name="crag",
    voted=[
        VoteDefinition(
            model_name="CragNameVote",
            collection_name="name_votes",
            item_name="name_vote",
            type=str,
        ),
        VoteDefinition(
            model_name="CragBannerVote",
            collection_name="banner_votes",
            item_name="banner_vote",
            type=UUID,
        ),
        VoteDefinition(
            model_name="AccessInformationVote",
            collection_name="access_information_votes",
            item_name="access_information_vote",
            type=str,
        ),
        VoteDefinition(
            model_name="CragDescriptionVote",
            collection_name="decription_votes",
            item_name="description_vote",
            type=str,
        ),
    ]
)
