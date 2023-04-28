from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.viewsets import ViewSet,GenericViewSet
from api.serializers import UserSerializer,ProfileSerializer,QuestionSerializer,AnswerSerializer
from rest_framework.mixins import CreateModelMixin
from rest_framework.generics import GenericAPIView
from stack.models import UserProfile,Questions,Answers
from rest_framework import authentication,permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers

# Create your views here.
# class UserView(ViewSet):
#     def create(self,request,*args,**kwargs):
#         serializer_class=UserSerializer
#         serializer=UserSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(data=serializer.data)
#         else:
#             return Response(data=serializer.errors)

class UsersView(GenericViewSet,CreateModelMixin):
    serializer_class=UserSerializer
    queryset=User.objects.all()

class ProfileView(ModelViewSet):
    serializer_class=ProfileSerializer
    queryset=UserProfile
    # authentication_classes=[authentication.TokenAuthentication]
    # permission_classes=[permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # def get_queryset(self):
    #     return UserProfile.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        prof=self.get_object()
        if prof.user != request.user:
            raise serializers.ValidationError("not allowed to perform")
        else:
            return super().destroy(request,*args,**kwargs)
    
    



class QuestionsView(ModelViewSet):
    serializer_class=QuestionSerializer
    queryset=Questions.objects.all()
    # authentication_classes=[authentication.TokenAuthentication]
    # permission_classes=[permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=["post"],detail=True)
    def add_answer(self,request,*args,**kwargs):
        serializer=AnswerSerializer(data=request.data)
        quest=self.get_object()
        user=request.user
        if serializer.is_valid():
            serializer.save(question=quest,user=user)
            return Response(data=serializer.data)
        else:
            return Response(data=serializer.errors)
        
    def destroy(self, request, *args, **kwargs):
        que=self.get_object()
        if que.user != request.user:
            raise serializers.ValidationError("not allowed to perform")
        else:
            return super().destroy(request,*args,**kwargs)

class AnswersView(ModelViewSet):
    serializer_class=AnswerSerializer
    queryset=Answers.objects.all()
    # authentication_classes=[authentication.TokenAuthentication]
    # permission_classes=[permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        raise serializers.ValidationError("method not allowed")
    
    @action(methods=["post"],detail=True)
    def add_upvote(self,request,*args,**kwargs):
        answer=self.get_object()
        answer.up_vote.add(request.user)
        answer.save()
        return Response(data="upvoted")
    
    @action(methods=["post"],detail=True)
    def down_vote(self,request,*args,**kwargs):
        answer=self.get_object()
        answer.up_vote.remove(request.user)
        answer.save()
        return Response(data="upvote removed")
    
    def destroy(self, request, *args, **kwargs):
        ans=self.get_object()
        if ans.user != request.user:
            raise serializers.ValidationError("Perform not allowed")
        else:
            return super().destroy(request,*args,**kwargs)