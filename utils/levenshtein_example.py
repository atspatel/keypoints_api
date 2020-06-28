# from django.db.models import Func

# class Levenshtein(Func):
#     template = "%(function)s(%(expressions)s, '%(search_term)s', 1, 2, 2)"
#     function = "levenshtein"

#     def __init__(self, expression, search_term, **extras):
#         super(Levenshtein, self).__init__(
#             expression,
#             search_term=search_term,
#             **extras
#         )

# Example
# KeywordsTag.objects.filter(key__icontains=suggestion_text
#                            ).annotate(lev_dist=Levenshtein(F('key'), suggestion_text)
#                                       ).filter(lev_dist__lte=10
#                                                ).order_by('lev_dist')
