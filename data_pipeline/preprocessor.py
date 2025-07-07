#!/usr/bin/env python3
"""
Advanced preprocessor for scraped data with review filtering
"""

import re
import hashlib
import logging
from typing import List, Dict, Any, Set, Tuple
from .config import PreprocessingConfig

logger = logging.getLogger(__name__)

class AdvancedPreprocessor:
    """Advanced preprocessing pipeline for scraped data"""
    
    def __init__(self, config: PreprocessingConfig):
        self.config = config
        self.stats = {
            'total_loaded': 0,
            'filtered_quality': 0,
            'filtered_duplicates': 0,
            'filtered_non_review': 0,
            'filtered_spam': 0,
            'processed_successfully': 0,
            'language_distribution': {},
            'source_distribution': {}
        }
        
        # Cache for duplicate detection
        self.seen_hashes: Set[str] = set()
        
        # Initialize review filtering patterns
        self._init_review_filters()
        
    def _calculate_text_hash(self, text: str) -> str:
        """Calculate hash for duplicate detection"""
        # Normalize text for hashing
        normalized = re.sub(r'\s+', ' ', text.lower().strip())
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _is_quality_text(self, text: str) -> bool:
        """Check if text meets quality requirements"""
        if not text or not text.strip():
            return False
        
        text = text.strip()
        
        # Length checks
        if len(text) < self.config.min_text_length or len(text) > self.config.max_text_length:
            return False
        
        # Word count check
        words = text.split()
        if len(words) < self.config.min_word_count:
            return False
        
        # Repetition check
        if len(words) > 1:
            unique_words = set(words)
            repetition_ratio = 1 - (len(unique_words) / len(words))
            if repetition_ratio > self.config.max_repetition_ratio:
                return False
        
        return True
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection for Vietnamese/English"""
        if not text:
            return 'unknown'
        
        # Vietnamese character patterns
        vietnamese_chars = r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđĐ]'
        vietnamese_count = len(re.findall(vietnamese_chars, text, re.IGNORECASE))
        vietnamese_ratio = vietnamese_count / len(text) if text else 0
        
        if vietnamese_ratio >= self.config.vietnamese_char_threshold:
            return 'vi'
        
        # English word detection
        english_words = re.findall(r'\b[a-zA-Z]+\b', text)
        english_ratio = len(english_words) / len(text.split()) if text.split() else 0
        
        if english_ratio >= self.config.english_word_threshold:
            return 'en'
        
        return 'mixed'
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text content"""
        if not text:
            return ''
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove excessive punctuation
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        text = re.sub(r'[.]{3,}', '...', text)
        
        # Basic text cleanup
        text = re.sub(r'https?://\S+', '[URL]', text)  # Replace URLs
        text = re.sub(r'\d{10,}', '[PHONE]', text)     # Replace phone numbers
        
        return text.strip()
    
    def _init_review_filters(self):
        """Initialize patterns for identifying non-review comments"""
        
        # Patterns for non-review content (Vietnamese and English)
        self.non_review_patterns = {
            'greeting_only': [
                r'^(hi|hello|hey|chào|xin chào|helo)\s*[!.]*\s*$',
                r'^(thanks?|thank you|cảm ơn|cam on|tks|ty)\s*[!.]*\s*$',
                r'^(bye|goodbye|tạm biệt|chào tạm biệt)\s*[!.]*\s*$'
            ],
            'short_reactions': [
                r'^(ok|okay|okie|oke|good|nice|tốt|hay|được)\s*[!.]*\s*$',
                r'^(wow|amazing|tuyệt|đỉnh|cool|ngon)\s*[!.]*\s*$',
                r'^(yes|no|có|không|ừ|uhm|hmm)\s*[!.]*\s*$'
            ],
            'spam_patterns': [
                r'(like và subscribe|like sub|đăng ký kênh)',
                r'(inbox|pm|liên hệ|contact|phone|zalo|facebook)',
                r'(bán|mua|sell|buy|giá rẻ|cheap|discount|khuyến mãi)',
                r'(link|website|web|shop|store|cửa hàng)',
                r'(\d{10,}|\d{3,4}[-.\s]\d{3,4}[-.\s]\d{3,4})',  # Phone numbers
                r'(facebook\.com|fb\.com|zalo|telegram|whatsapp)'
            ],
            'question_seeking_help': [
                r'^(help|giúp|hỏi|ask|question|câu hỏi)',
                r'(how to|làm sao|làm thế nào|hướng dẫn|guide)',
                r'(where|đâu|ở đâu|tìm ở đâu|mua ở đâu)',
                r'(when|khi nào|bao giờ|lúc nào)'
            ],
            'off_topic': [
                r'(first|đầu tiên|1st|đầu|ai xem đầu)',
                r'(early|sớm|view sớm|xem sớm)',
                r'(music|nhạc|bài hát|song|beat)',
                r'(movie|phim|film|video clip|mv)'
            ],
            'emotional_only': [
                r'^[😀-🙏🤔-🤯😭-😱🥰-🥵]+\s*$',  # Only emojis
                r'^(haha|hihi|huhu|hoho)+\s*[!.]*\s*$',
                r'^(lol|lmao|omg|wtf|wth)\s*[!.]*\s*$'
            ]
        }
        
        # Patterns that indicate genuine reviews
        self.review_indicators = [
            r'(sử dụng|dùng|use|used|using)',
            r'(chất lượng|quality|tốt|xấu|good|bad|nice)',
            r'(giá|price|cost|expensive|cheap|rẻ|đắt)',
            r'(mua|buy|bought|purchase|order|đặt hàng)',
            r'(giao hàng|ship|delivery|nhận hàng|packaging)',
            r'(recommend|đề xuất|khuyên|should|nên)',
            r'(experience|trải nghiệm|cảm nhận|feel|cảm giác)',
            r'(so sánh|compare|comparison|khác|different)',
            r'(đánh giá|review|rate|rating|star|sao)',
            r'(ưu điểm|nhược điểm|pros|cons|advantage|disadvantage)',
            r'(màu sắc|color|size|kích thước|design|thiết kế)',
            r'(pin|battery|charge|sạc|điện)',
            r'(camera|ảnh|photo|picture|video|quay)',
            r'(âm thanh|sound|speaker|loa|music|nhạc)'
        ]
        
        # Enhanced patterns for strict product experience filtering
        self.product_experience_indicators = [
            r'(đã mua|đã dùng|đã thử|bought|used|tried)',
            r'(lên môi|apply|wear|khi dùng|when using|after using)',
            r'(chất son|texture|độ bền|lasting|smudge|fade)',
            r'(khô môi|dry lips|moisturizing|dưỡng ẩm|comfortable)',
            r'(pigment|màu sắc thực tế|actual color|lên màu|color payoff)',
            r'(trải nghiệm thực tế|actual experience|thực sự|really|actually)',
            r'(sau khi|after|before|trước khi|trong quá trình|during)',
            r'(cảm giác|feel|feeling|touch|cầm nắm|grip)',
            r'(hiệu suất|performance|tốc độ|speed|lag|smooth)',
            r'(pin|battery life|sạc|charging|runtime|standby)'
        ]
        
        # Patterns for non-product content (videos, marketing, etc.)
        self.non_product_content_patterns = [
            r'(video|vid|swatch|clip|recording|filming|camera|youtube|channel)',
            r'(giveaway|ga|ctkm|khuyến mãi|tặng|mua|giảm giá|promotion)',
            r'(thank|cảm ơn|thanks|thích video|love video|subscribe)',
            r'(áo|váy|outfit|trang phục|clothes|fashion)',
            r'(info|infor|link|http|bit\.ly|shop|mua ở đâu|where to buy)',
            r'(màu nào|which color|chọn màu|pick color|undertone)',
            r'(ai xem|who watch|view|lượt xem|viewer|follower)',
            r'(unboxing|mở hộp|first impression|ấn tượng đầu)',
            r'(tutorial|hướng dẫn|how to|làm thế nào|guide)',
            r'(demo|demonstration|thử|test|sample|mẫu thử)'
        ]
    
    def _is_review_content(self, text: str) -> Tuple[bool, str]:
        """
        Determine if text is a genuine review or just a non-review comment
        Returns: (is_review, reason_if_not)
        """
        if not text or not text.strip():
            return False, "empty_text"
        
        text_lower = text.lower()
        
        # Check for spam patterns first
        for pattern in self.non_review_patterns['spam_patterns']:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return False, "spam_content"
        
        # Check for greeting-only comments
        for pattern in self.non_review_patterns['greeting_only']:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return False, "greeting_only"
        
        # Check for short reactions
        for pattern in self.non_review_patterns['short_reactions']:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return False, "short_reaction"
        
        # Check for question-seeking help
        for pattern in self.non_review_patterns['question_seeking_help']:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return False, "help_seeking"
        
        # Check for off-topic comments
        for pattern in self.non_review_patterns['off_topic']:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return False, "off_topic"
        
        # Check for emotional-only comments
        for pattern in self.non_review_patterns['emotional_only']:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return False, "emotional_only"
        
        # Check for non-product content (videos, marketing, etc.)
        for pattern in self.non_product_content_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return False, "non_product_content"
        
        # Count review indicators
        review_score = 0
        for pattern in self.review_indicators:
            if re.search(pattern, text_lower, re.IGNORECASE):
                review_score += 1
        
        # Count product experience indicators for stricter filtering
        product_experience_score = 0
        for pattern in self.product_experience_indicators:
            if re.search(pattern, text_lower, re.IGNORECASE):
                product_experience_score += 1
        
        # Check minimum length for potential reviews
        word_count = len(text.split())
        
        # Apply enhanced review scoring logic with product experience
        if word_count < 5:
            if review_score == 0 and product_experience_score == 0:
                return False, "too_short_no_indicators"
        elif word_count < 10:
            if review_score < 1 and product_experience_score == 0:
                return False, "short_insufficient_indicators"
        elif word_count >= 10:
            # For longer reviews, require at least one product experience indicator
            # This is the key enhancement to filter out video reviews and marketing content
            if product_experience_score == 0 and review_score < 2:
                return False, "insufficient_product_experience"
        
        return True, "valid_review"
    
    def _detect_spam(self, text: str) -> bool:
        """Enhanced spam detection"""
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Check for excessive repetition
        words = text_lower.split()
        if len(words) > 3:
            unique_words = set(words)
            repetition_ratio = 1 - (len(unique_words) / len(words))
            if repetition_ratio > 0.7:  # More than 70% repetition
                return True
        
        # Check for excessive punctuation or caps
        if len(text) > 10:
            caps_ratio = sum(1 for c in text if c.isupper()) / len(text)
            punct_ratio = sum(1 for c in text if c in '!?.,;:') / len(text)
            if caps_ratio > 0.6 or punct_ratio > 0.3:
                return True
        
        # Check for promotional content
        promotional_patterns = [
            r'(follow|theo dõi|đăng ký|subscribe)',
            r'(sale|giảm giá|promotion|khuyến mãi)',
            r'(free|miễn phí|gift|quà tặng)',
            r'(win|thắng|lucky|may mắn|trúng thưởng)'
        ]
        
        promotional_count = 0
        for pattern in promotional_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                promotional_count += 1
        
        return promotional_count >= 2
    
    def process_data(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process scraped data through the preprocessing pipeline"""
        self.stats['total_loaded'] = len(raw_data)
        
        processed_items = []
        
        for item in raw_data:
            try:
                # Extract content
                content = item.get('content', '')
                
                # Quality filtering
                if not self._is_quality_text(content):
                    self.stats['filtered_quality'] += 1
                    continue
                
                # Duplicate detection
                if self.config.enable_deduplication:
                    text_hash = self._calculate_text_hash(content)
                    if text_hash in self.seen_hashes:
                        self.stats['filtered_duplicates'] += 1
                        continue
                    self.seen_hashes.add(text_hash)
                
                # Normalize content
                normalized_content = self._normalize_text(content)
                
                # Detect language
                language = self._detect_language(normalized_content)
                
                # Review filtering
                is_review, _ = self._is_review_content(normalized_content)
                if not is_review:
                    self.stats['filtered_non_review'] += 1
                    continue
                
                # Create processed item
                processed_item = {
                    'id': item.get('id', ''),
                    'content': normalized_content,
                    'source': item.get('source', 'unknown'),
                    'language': language,
                    'created_at': item.get('created_at', ''),
                    'metadata': item
                }
                
                processed_items.append(processed_item)
                self.stats['processed_successfully'] += 1
                
                # Update statistics
                source = item.get('source', 'unknown')
                self.stats['source_distribution'][source] = self.stats['source_distribution'].get(source, 0) + 1
                self.stats['language_distribution'][language] = self.stats['language_distribution'].get(language, 0) + 1
                
            except Exception as e:
                logger.error(f"Error processing item: {e}")
                continue
        
        return {
            'processed_data': processed_items,
            'stats': self.stats,
            'config': {
                'min_text_length': self.config.min_text_length,
                'max_text_length': self.config.max_text_length,
                'enable_deduplication': self.config.enable_deduplication,
                'target_language': self.config.target_language
            }
        }
