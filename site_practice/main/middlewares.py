from .models import SubRubric


def bboard_context_processor(request):      # 33.3
    context = {}
    context['rubrics'] = SubRubric.objects.all()
    return context

