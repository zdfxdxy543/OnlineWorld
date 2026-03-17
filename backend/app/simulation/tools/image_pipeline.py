from app.simulation.tools.workflow import AbstractCapabilityWorkflow
from app.simulation.protocol import (
    ActionRequest, FactExecutionResult, ContentGenerationRequest, GeneratedContent, ConsistencyCheckResult, PublicationResult, CapabilitySpec, StoryEvent
)
import requests
import os
from uuid import uuid4
        )
# 假设硅基流动平台API配置
SILICONFLOW_API_URL = "https://api.siliconflow.com/v1/generate-image"
# 用于容器注册的工具执行器
from app.simulation.tools.workflow import FiveStageToolExecutor

class ImagePipelineToolExecutor(FiveStageToolExecutor):
    def __init__(self, content_generator):
        super().__init__(workflows=[ImageGenerationWorkflow()], content_generator=content_generator)
SILICONFLOW_API_KEY = os.environ.get("SILICONFLOW_API_KEY", "your_api_key_here")
IMAGE_SAVE_DIR = "storage/netdisk/ai_images/"

os.makedirs(IMAGE_SAVE_DIR, exist_ok=True)

class ImageGenerationWorkflow(AbstractCapabilityWorkflow):
    @property
    def capability(self) -> CapabilitySpec:
        return CapabilitySpec(
            name="image.generate",
            site="ai_image",
            description="使用硅基流动平台大模型API生成图片并保存本地",
            input_schema={
                "prompt": "string",
                "width": "integer optional",
                "height": "integer optional"
            },
            read_only=False,
        )

    def execute_facts(self, request: ActionRequest) -> FactExecutionResult:
        prompt = str(request.payload.get("prompt", "")).strip()
        width = int(request.payload.get("width", 512))
        height = int(request.payload.get("height", 512))
        draft_id = str(uuid4())
        return FactExecutionResult(
            capability=request.capability,
            site="ai_image",
            actor_id=request.actor_id,
            facts=[f"图片生成草稿={draft_id}"],
            events=[
                StoryEvent(
                    name="WorldActionExecuted",
                    detail="图片生成草稿已创建，等待内容生成。",
                    metadata={"draft_id": draft_id},
                )
            ],
            output={"draft_id": draft_id, "status": "draft_created"},
            generation_context={
                "draft_id": draft_id,
                "prompt": prompt,
                "width": width,
                "height": height,
            },
            requires_content_generation=True,
        )

    def build_generation_request(self, request: ActionRequest, fact_result: FactExecutionResult) -> ContentGenerationRequest:
        return ContentGenerationRequest(
            capability=request.capability,
            site="ai_image",
            actor_id=request.actor_id,
            instruction="根据prompt生成一张图片，返回base64编码或图片URL。",
            desired_fields=["image_data", "image_url"],
            fact_context=fact_result.generation_context,
            style_context={"format": "image", "language": "zh"},
        )

    def validate_generated_content(self, request: ActionRequest, fact_result: FactExecutionResult, generated_content: GeneratedContent) -> ConsistencyCheckResult:
        fields = generated_content.fields
        image_data = fields.get("image_data")
        image_url = fields.get("image_url")
        violations = []
        if not image_data and not image_url:
            violations.append("missing-field:image_data_or_url")
        return ConsistencyCheckResult(
            passed=not violations,
            violations=violations,
            normalized_fields={"image_data": image_data, "image_url": image_url},
        )

    def publish(self, request: ActionRequest, fact_result: FactExecutionResult, validation_result: ConsistencyCheckResult) -> PublicationResult:
        import base64
        draft_id = fact_result.output["draft_id"]
        image_data = validation_result.normalized_fields.get("image_data")
        image_url = validation_result.normalized_fields.get("image_url")
        file_name = f"ai_image_{draft_id}.png"
        local_path = os.path.join(IMAGE_SAVE_DIR, file_name)
        if image_data:
            with open(local_path, "wb") as f:
                f.write(base64.b64decode(image_data))
        elif image_url:
            resp = requests.get(image_url)
            with open(local_path, "wb") as f:
                f.write(resp.content)
        else:
            raise ValueError("No image data to save.")
        return PublicationResult(
            output={
                "draft_id": draft_id,
                "file_name": file_name,
                "local_path": local_path,
                "image_url": f"/api/ai_image/{file_name}",
                "publication_status": "published",
            },
            facts=[f"已生成图片={file_name}"],
            events=[
                StoryEvent(
                    name="ContentPublished",
                    detail="AI图片已生成并保存到本地。",
                    metadata={"file_name": file_name, "local_path": local_path},
                )
            ],
        )
