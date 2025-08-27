"""
Enhanced dialogue extraction service to handle complex LLM responses.
"""

import re
import json
from typing import Dict, List, Any, Optional
from loguru import logger


class DialogueExtractor:
    """
    Advanced dialogue extraction that handles various LLM response formats.
    """
    
    @staticmethod
    def extract_all_panels_robust(text: str) -> Dict[int, str]:
        """
        Extract dialogue from all panels using multiple parsing strategies.
        
        Args:
            text: Raw LLM response text
            
        Returns:
            Dictionary mapping panel number to dialogue text
        """
        panels = {}
        
        # Strategy 1: Standard format with quotes
        strategy1_pattern = r'PANEL_(\d+):\s*dialogue_text:\s*"([^"]*)"'
        matches = re.findall(strategy1_pattern, text, re.DOTALL)
        for panel_num, dialogue in matches:
            if dialogue.strip() and len(dialogue.strip()) > 10:
                panels[int(panel_num)] = dialogue.strip()
        
        # Strategy 2: Format without quotes
        if len(panels) < 6:
            strategy2_pattern = r'PANEL_(\d+):\s*dialogue_text:\s*([^\n]+)'
            matches = re.findall(strategy2_pattern, text, re.DOTALL)
            for panel_num, dialogue in matches:
                panel_int = int(panel_num)
                if panel_int not in panels and dialogue.strip() and len(dialogue.strip()) > 10:
                    panels[panel_int] = dialogue.strip()
        
        # Strategy 3: More flexible pattern
        if len(panels) < 6:
            strategy3_pattern = r'PANEL\s*(\d+)[:\s]*.*?dialogue[_\s]*text[:\s]*["\']?([^"\'\n]+)["\']?'
            matches = re.findall(strategy3_pattern, text, re.DOTALL | re.IGNORECASE)
            for panel_num, dialogue in matches:
                panel_int = int(panel_num)
                if panel_int not in panels and dialogue.strip() and len(dialogue.strip()) > 10:
                    panels[panel_int] = dialogue.strip()
        
        # Strategy 4: Look for numbered dialogue blocks
        if len(panels) < 6:
            strategy4_pattern = r'(\d+)[\.:\s]+([^0-9\n][^\n]{20,})'
            matches = re.findall(strategy4_pattern, text, re.DOTALL)
            panel_counter = 1
            for num_str, dialogue in matches:
                if panel_counter <= 6 and panel_counter not in panels:
                    clean_dialogue = dialogue.strip().rstrip('.')
                    if len(clean_dialogue) > 15:
                        panels[panel_counter] = clean_dialogue
                        panel_counter += 1
        
        logger.info(f"Extracted dialogue for {len(panels)} panels using robust extraction")
        return panels
    
    @staticmethod
    def validate_and_enhance_dialogue(panels: Dict[int, str], inputs: Any) -> Dict[int, str]:
        """
        Validate extracted dialogue and enhance with meaningful content if needed.
        
        Args:
            panels: Extracted panel dialogue
            inputs: Story inputs for fallback generation
            
        Returns:
            Enhanced panel dialogue dictionary
        """
        enhanced_panels = {}
        name = getattr(inputs, 'nickname', 'our hero') if inputs else 'our hero'
        dream = getattr(inputs, 'dream', 'their goals') if inputs else 'their goals'
        mood = getattr(inputs, 'mood', 'uncertain') if inputs else 'uncertain'
        
        # Meaningful fallback content
        fallback_dialogues = {
            1: f"Meet {name}. They're feeling {mood} today, but deep inside burns a desire to achieve {dream}. Every great journey begins with a single step forward.",
            2: f"{name} faces the challenge ahead. The path to {dream} isn't easy, but they've come too far to give up now. Sometimes the hardest battles are the ones we fight within ourselves.",
            3: f"Taking a moment to breathe, {name} reflects on how far they've already come. Even when feeling {mood}, there's strength in acknowledging both struggles and progress.",
            4: f"In this moment of clarity, {name} discovers something important. Their {dream} isn't just about the destination - it's about becoming the person they're meant to be along the way.",
            5: f"With newfound determination, {name} takes action. They realize that being {mood} doesn't define them - it's just one part of their story, and they have the power to write the next chapter.",
            6: f"Looking back on the journey, {name} sees how much they've grown. The road to {dream} continues, but now they know they have the strength to face whatever comes next. Hope lights the way forward."
        }
        
        for panel_num in range(1, 7):
            if panel_num in panels and len(panels[panel_num]) > 20:
                # Use extracted dialogue if it's substantial
                enhanced_panels[panel_num] = panels[panel_num]
            else:
                # Use meaningful fallback
                enhanced_panels[panel_num] = fallback_dialogues[panel_num]
                logger.info(f"Using enhanced fallback dialogue for panel {panel_num}")
        
        return enhanced_panels


# Global instance
dialogue_extractor = DialogueExtractor()
