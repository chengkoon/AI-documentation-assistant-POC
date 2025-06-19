package com.aiassistant.controller;

import com.aiassistant.api.PostsApi;
import com.aiassistant.api.model.Post;
import com.aiassistant.service.PostService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequiredArgsConstructor
public class PostController implements PostsApi {
    
    private final PostService postService;
    
    @Override
    public ResponseEntity<List<Post>> getAllPosts() {
        List<Post> posts = postService.getAllPosts();
        return ResponseEntity.ok(posts);
    }
}
