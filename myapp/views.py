from django.shortcuts import render, resolve_url, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView, CreateView, DetailView, UpdateView, DeleteView, ListView
from django.views.generic.edit import DeleteView
from .models import Post, Like, Category
from django.urls import reverse_lazy
from .forms import PostForm, LoginForm, SingUpForm, SearchForm
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q


class OnluMyPostMixin(UserPassesTestMixin):
    reaise_exception = True
    def test_func(self):
        post = Post.objects.get(id = self.kwargs['pk'])
        return post.author == self.request.user

class Index(TemplateView):
    template_name = "myapp/index.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        post_list = Post.objects.all().order_by('-created_at')
        context = {
            'post_list': post_list,
        }
        return context

class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('myapp:index')

    def form_valid(self, form):
        form.instance.author_id = self.request.user.id
        return super(PostCreate, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, ('Postを登録しました'))
        return resolve_url('myapp:index')

class PostDetail(DetailView):
    model = Post
    
    def get_context_data(self, *args, **kwargs):
        detail_data = Post.objects.get(id= self.kwargs['pk'])
        category_posts = Post.objects.filter(category = detail_data.category).order_by('-created_at')[:5]
        
        params = {
            'object': detail_data,
            'category_posts': category_posts
        }

        return params

class PostUpdate(OnluMyPostMixin, UpdateView):
    model = Post
    form_class = PostForm

    def get_success_url(self):
        messages.info(self.request, 'Postを更新しました。')
        return resolve_url('myapp:post_detail', pk=self.kwargs['pk'])

class PostDelete(OnluMyPostMixin, DeleteView):
    model = Post

    def get_success_url(self):
        messages.info(self.request, 'Postを削除しました')
        return resolve_url('myapp:index')

class PostList(ListView):
    model = Post

    def get_queryset(self):
        return Post.objects.all().order_by('-created_at')

# ログイン機能
class Login(LoginView):
    form_class = LoginForm
    template_name = 'myapp/login.html'

class Logout(LogoutView):
    template_name = 'myapp/logout.html'

class SingUp(CreateView):
    form_class = SingUpForm
    template_name = 'myapp/singup.html'
    success_url = reverse_lazy('myapp:index')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        self.object = user

        messages.info(self.request, 'ユーザーを登録しました。')
        return HttpResponseRedirect(self.get_success_url())

@login_required
def Like_add(request, post_id):
    post = Post.objects.get(id = post_id)

    like = Like.objects.filter(user = request.user, post = post_id)
    if like.exists():
        like.delete()
        messages.info(request, 'いいねを削除しました')
        return redirect('myapp:post_detail', post.id)

    like = Like()
    like.user = request.user
    like.post = post
    like.save()

    messages.success(request, 'お気に入りを追加しました!')
    return redirect('myapp:post_detail', post.id)

class CategoryList(ListView):
    model = Category

class CategoryDetail(DetailView):
    model = Category
    slug_field = 'name_en'
    slug_url_kwarg = 'name_en'

    def get_context_data(self, *args, **kwargs):
        detail_data = Category.objects.get(name_en = self.kwargs['name_en'])
        category_posts = Post.objects.filter(category = detail_data).order_by('-created_at')

        params = {
            'object': detail_data,
            'category_posts': category_posts,
        }
            
        return params
        
def Search(request):
    if request.method == 'POST':
        searchform = SearchForm(request.POST)

        if searchform.is_valid():
            freeword = searchform.cleaned_data['freeword']
            search_list = Post.objects.filter(Q(title__icontains = freeword) |Q(content__icontains = freeword))

        params = {
            'search_list': search_list,
        }

        return render(request, 'myapp/search.html', params)