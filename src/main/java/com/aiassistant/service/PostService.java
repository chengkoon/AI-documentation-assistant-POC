package com.aiassistant.service;

import com.aiassistant.repository.PostRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.ZoneOffset;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class PostService {
    
    private final PostRepository postRepository;
    
    public List<com.aiassistant.api.model.Post> getAllPosts() {
        List<com.aiassistant.entity.Post> entities = postRepository.findAll();
        return entities.stream()
                .map(this::convertToApiModel)
                .collect(Collectors.toList());
    }
    
    private com.aiassistant.api.model.Post convertToApiModel(com.aiassistant.entity.Post entity) {
        com.aiassistant.api.model.Post post = new com.aiassistant.api.model.Post();
        post.setId(entity.getId());
        post.setTitle(entity.getTitle());
        post.setContent(entity.getContent());
        
        if (entity.getCreatedAt() != null) {
            post.setCreatedAt(entity.getCreatedAt().atOffset(ZoneOffset.UTC));
        }
        
        if (entity.getUpdatedAt() != null) {
            post.setUpdatedAt(entity.getUpdatedAt().atOffset(ZoneOffset.UTC));
        }
        
        return post;
    }
}
