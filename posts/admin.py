from django.contrib import admin

from posts.models import *



# class PostImage(admin.TabularInline):
#     model = PostImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


# @admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'type', 'category', 'sub_category', 'detail', 'thumbnail',)
    search_fields = ('author__name', 'author__username', 'author__email', 'detail', )

    # inlines = [PostImage,]


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('author_id', 'post', 'images')

    class Meta:
        model = Gallery
        verbose_name = 'Gallery'
        verbose_name_plural = 'Gallery'

admin.site.register(ReportedPost)
admin.site.register(ReportedGroupPost)
admin.site.register(GroupPostLike)
admin.site.register(GroupPostDislike)
admin.site.register(Comment)
admin.site.register(CommentLike)
admin.site.register(CommentDislike)
admin.site.register(Notification)


admin.site.register(WorkProposal)
admin.site.register(HireComment)
admin.site.register(BuyProposals)
admin.site.register(SellProposals)
admin.site.register(Type)
admin.site.register(PromotionalDetail)
admin.site.register(DefaultImage)
admin.site.register(UserGroup)
admin.site.register(GroupPost)
admin.site.register(RatingFeedback)
admin.site.register(PostRating)
admin.site.register(UserInterest)

admin.site.register(Post,PostAdmin)
admin.site.register(PostImage)

