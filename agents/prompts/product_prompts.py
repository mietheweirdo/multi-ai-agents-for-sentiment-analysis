"""
Product-category-specific prompt customizations for different product types.
Each product category has specialized focus areas for better analysis.
"""

from typing import Dict, List, Any

class ProductPrompts:
    """Product-category-specific prompt customizations"""
    
    # Product category focus areas
    PRODUCT_FOCUS_AREAS = {
        "electronics": {
            "quality_focus": [
                "Product durability and build quality",
                "Technical performance and reliability",
                "Battery life and power efficiency",
                "Screen quality and display performance",
                "Hardware specifications and capabilities"
            ],
            "experience_focus": [
                "Customer service and technical support",
                "Delivery and packaging quality",
                "Warranty and return process",
                "Installation and setup experience",
                "Post-purchase support quality"
            ],
            "user_experience_focus": [
                "Ease of use and user interface",
                "Design aesthetics and ergonomics",
                "Feature satisfaction and innovation",
                "Overall user satisfaction",
                "Lifestyle integration and convenience"
            ],
            "business_focus": [
                "Market competitiveness and positioning",
                "Value for money and pricing strategy",
                "Brand reputation and trust",
                "Customer retention potential",
                "Market differentiation opportunities"
            ],
            "technical_focus": [
                "Technical specifications and features",
                "Performance benchmarks and capabilities",
                "Compatibility and integration",
                "Software and firmware quality",
                "Technical innovation and advancement"
            ]
        },
        
        "fashion": {
            "quality_focus": [
                "Fabric quality and material durability",
                "Stitching and construction quality",
                "Fit and sizing accuracy",
                "Color fastness and maintenance",
                "Overall craftsmanship and finish"
            ],
            "experience_focus": [
                "Customer service and styling advice",
                "Delivery and packaging presentation",
                "Return and exchange process",
                "Size recommendations and fitting",
                "Post-purchase care instructions"
            ],
            "user_experience_focus": [
                "Style and design appeal",
                "Comfort and wearability",
                "Versatility and styling options",
                "Confidence and self-expression",
                "Overall satisfaction and happiness"
            ],
            "business_focus": [
                "Fashion trend alignment",
                "Price positioning and value perception",
                "Brand image and reputation",
                "Customer loyalty potential",
                "Market differentiation and uniqueness"
            ],
            "technical_focus": [
                "Fabric technology and innovation",
                "Design features and functionality",
                "Care requirements and maintenance",
                "Sustainability and eco-friendliness",
                "Technical performance aspects"
            ]
        },
        
        "home_garden": {
            "quality_focus": [
                "Material quality and durability",
                "Construction and assembly quality",
                "Functionality and performance",
                "Safety and reliability",
                "Long-term value and longevity"
            ],
            "experience_focus": [
                "Customer service and advice",
                "Delivery and installation service",
                "Assembly instructions and support",
                "Warranty and maintenance service",
                "Post-purchase guidance and care"
            ],
            "user_experience_focus": [
                "Aesthetic appeal and design",
                "Ease of use and convenience",
                "Comfort and satisfaction",
                "Lifestyle integration",
                "Overall enjoyment and fulfillment"
            ],
            "business_focus": [
                "Home improvement market positioning",
                "Value for money and investment",
                "Brand trust and reliability",
                "Customer satisfaction potential",
                "Market demand and trends"
            ],
            "technical_focus": [
                "Technical specifications and features",
                "Performance capabilities and efficiency",
                "Innovation and technology integration",
                "Safety features and compliance",
                "Technical value and advancement"
            ]
        },
        
        "beauty_health": {
            "quality_focus": [
                "Product effectiveness and results",
                "Ingredient quality and safety",
                "Skin compatibility and reactions",
                "Longevity and shelf life",
                "Overall product performance"
            ],
            "experience_focus": [
                "Customer service and consultation",
                "Delivery and packaging quality",
                "Return and refund process",
                "Usage guidance and support",
                "Post-purchase care advice"
            ],
            "user_experience_focus": [
                "Sensory experience and satisfaction",
                "Confidence and self-esteem impact",
                "Ease of application and use",
                "Results and transformation",
                "Overall happiness and satisfaction"
            ],
            "business_focus": [
                "Beauty industry positioning",
                "Value for money and pricing",
                "Brand reputation and trust",
                "Customer loyalty potential",
                "Market trends and demand"
            ],
            "technical_focus": [
                "Formulation and ingredient technology",
                "Scientific backing and research",
                "Safety and regulatory compliance",
                "Innovation and advancement",
                "Technical performance metrics"
            ]
        },
        
        "sports_outdoors": {
            "quality_focus": [
                "Durability and ruggedness",
                "Performance and reliability",
                "Safety and protection features",
                "Weather resistance and adaptability",
                "Long-term functionality"
            ],
            "experience_focus": [
                "Customer service and expertise",
                "Delivery and packaging",
                "Return and warranty process",
                "Usage guidance and training",
                "Post-purchase support"
            ],
            "user_experience_focus": [
                "Performance satisfaction",
                "Comfort and fit",
                "Adventure and excitement",
                "Confidence and empowerment",
                "Overall enjoyment and achievement"
            ],
            "business_focus": [
                "Sports market positioning",
                "Value for money and investment",
                "Brand reputation and trust",
                "Customer loyalty potential",
                "Market trends and demand"
            ],
            "technical_focus": [
                "Technical specifications and features",
                "Performance capabilities and metrics",
                "Innovation and technology",
                "Safety and protection technology",
                "Technical advancement and features"
            ]
        },
        
        "books_media": {
            "quality_focus": [
                "Content quality and depth",
                "Production and presentation quality",
                "Accuracy and reliability",
                "Educational value and insight",
                "Overall content excellence"
            ],
            "experience_focus": [
                "Customer service and recommendations",
                "Delivery and packaging",
                "Return and exchange process",
                "Reading guidance and support",
                "Post-purchase engagement"
            ],
            "user_experience_focus": [
                "Entertainment and engagement",
                "Educational value and learning",
                "Emotional connection and impact",
                "Inspiration and motivation",
                "Overall satisfaction and fulfillment"
            ],
            "business_focus": [
                "Media market positioning",
                "Value for money and pricing",
                "Author/publisher reputation",
                "Customer loyalty potential",
                "Market trends and demand"
            ],
            "technical_focus": [
                "Content structure and organization",
                "Technical accuracy and detail",
                "Innovation in presentation",
                "Accessibility and usability",
                "Technical quality and standards"
            ]
        }
    }
    
    @staticmethod
    def get_product_focus_areas(product_category: str) -> Dict[str, List[str]]:
        """Get product-specific focus areas for a category"""
        return ProductPrompts.PRODUCT_FOCUS_AREAS.get(
            product_category.lower(), 
            ProductPrompts.PRODUCT_FOCUS_AREAS["electronics"]  # Default fallback
        )
    
    @staticmethod
    def customize_agent_prompt(base_prompt: str, product_category: str, agent_type: str) -> str:
        """Customize a base agent prompt with product-specific focus areas"""
        
        product_focus = ProductPrompts.get_product_focus_areas(product_category)
        focus_key = f"{agent_type}_focus"
        
        if focus_key not in product_focus:
            return base_prompt
        
        focus_areas = product_focus[focus_key]
        focus_text = "\n".join([f"- {area}" for area in focus_areas])
        
        # Insert product-specific focus areas into the prompt
        category_context = f"""
PRODUCT CATEGORY: {product_category.upper()}

For {product_category} products, pay special attention to:
{focus_text}

"""
        
        # Insert the category context after the base system message
        if "Focus your analysis on:" in base_prompt:
            # Replace the generic focus areas with product-specific ones
            lines = base_prompt.split('\n')
            new_lines = []
            in_focus_section = False
            
            for line in lines:
                if "Focus your analysis on:" in line:
                    new_lines.append(line)
                    new_lines.append(category_context)
                    in_focus_section = True
                elif in_focus_section and line.strip().startswith('-'):
                    continue  # Skip generic focus areas
                elif in_focus_section and not line.strip().startswith('-') and line.strip():
                    in_focus_section = False
                    new_lines.append(line)
                else:
                    new_lines.append(line)
            
            return '\n'.join(new_lines)
        else:
            # If no focus section found, add the category context
            return base_prompt.replace(
                "Analyze the given review",
                f"{category_context}Analyze the given review"
            )
    
    @staticmethod
    def get_available_categories() -> List[str]:
        """Get list of available product categories"""
        return list(ProductPrompts.PRODUCT_FOCUS_AREAS.keys())
    
    @staticmethod
    def add_custom_category(category_name: str, focus_areas: Dict[str, List[str]]):
        """Add a custom product category with its focus areas"""
        ProductPrompts.PRODUCT_FOCUS_AREAS[category_name.lower()] = focus_areas
    
    @staticmethod
    def get_category_description(category: str) -> str:
        """Get a description of what each product category focuses on"""
        
        descriptions = {
            "electronics": "Electronic devices, gadgets, and technology products",
            "fashion": "Clothing, accessories, and fashion items",
            "home_garden": "Home improvement, furniture, and garden products",
            "beauty_health": "Beauty products, health supplements, and wellness items",
            "sports_outdoors": "Sports equipment, outdoor gear, and fitness products",
            "books_media": "Books, digital media, and educational content"
        }
        
        return descriptions.get(category.lower(), f"Custom category: {category}") 