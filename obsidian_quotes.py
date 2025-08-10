import os
import random
import re
from pathlib import Path

class ObsidianQuoteDisplay:
    def __init__(self, books_directory):
        self.books_directory = Path(books_directory)
        if not self.books_directory.exists():
            raise FileNotFoundError(f"Directory '{books_directory}' not found!")
    
    def get_markdown_files(self):
        """Get all markdown files from the Books directory"""
        return list(self.books_directory.glob("*.md"))
    
    def extract_book_title(self, content):
        """Extract the first H1 heading as the book title"""
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()  # Remove '# ' prefix
        return "Unknown Book"
    
    def is_markup_only(self, line):
        """Check if a line contains only markup elements and no substantial text"""
        cleaned = line
        
        # Remove various markup patterns one by one
        cleaned = re.sub(r'!\[\[.*?\]\]', '', cleaned)      # Image embeds
        cleaned = re.sub(r'!rw-\w+', '', cleaned)           # Readwise elements
        cleaned = re.sub(r'\[\[.*?\]\]', '', cleaned)       # Wiki links
        cleaned = re.sub(r'\[.*?\]\(.*?\)', '', cleaned)    # Markdown links
        cleaned = re.sub(r'`.*?`', '', cleaned)             # Inline code
        cleaned = re.sub(r'\*\*.*?\*\*', '', cleaned)       # Bold
        cleaned = re.sub(r'\*.*?\*', '', cleaned)           # Italic
        cleaned = re.sub(r'==.*?==', '', cleaned)           # Highlights
        cleaned = re.sub(r'%%.*?%%', '', cleaned)           # Comments
        cleaned = re.sub(r'<!--.*?-->', '', cleaned)        # HTML comments
        cleaned = re.sub(r'<.*?>', '', cleaned)             # HTML tags
        cleaned = re.sub(r'#{1,6}\s*', '', cleaned)         # Headers
        cleaned = re.sub(r'^>\s*', '', cleaned)             # Blockquotes
        cleaned = re.sub(r'^[-*+]\s*', '', cleaned)         # List items
        cleaned = re.sub(r'^\d+\.\s*', '', cleaned)         # Numbered lists
        cleaned = re.sub(r'^---+$', '', cleaned)            # Horizontal rules
        
        # Check if what remains is substantial text
        cleaned = cleaned.strip()
        return len(cleaned) < 20 or not any(c.isalpha() for c in cleaned)
    
    def extract_paragraphs(self, content):
        """Extract paragraphs from markdown content, excluding headings, frontmatter, and empty lines"""
        lines = content.split('\n')
        paragraphs = []
        current_paragraph = []
        
        # Skip YAML frontmatter
        in_frontmatter = False
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Handle YAML frontmatter
            if i == 0 and line_stripped == '---':
                in_frontmatter = True
                continue
            elif in_frontmatter and line_stripped == '---':
                in_frontmatter = False
                continue
            elif in_frontmatter:
                continue
            
            # Skip various markdown and Readwise elements
            skip_conditions = [
                line_stripped.startswith('#'),
                line_stripped == '',
                line_stripped.startswith('```'),
                line_stripped.startswith('>'),
                line_stripped.startswith('- '),
                line_stripped.startswith('* '),
                line_stripped.startswith('1. '),
                line_stripped.startswith('![['),
                line_stripped.startswith('!rw-'),
                line_stripped.startswith('!['),
                line_stripped == '---',
                line_stripped.startswith('=='),
                line_stripped.startswith('%%'),
                line_stripped.startswith('<!--'),
                line_stripped.startswith('<'),
                (line_stripped.startswith('[[') and line_stripped.endswith(']]') and len(line_stripped) < 50)
            ]
            
            if any(skip_conditions):
                # If we have accumulated text, save it as a paragraph
                if current_paragraph:
                    paragraph_text = ' '.join(current_paragraph).strip()
                    if len(paragraph_text) > 100:
                        paragraphs.append(paragraph_text)
                    current_paragraph = []
                continue
            
            # Only add lines that contain substantial text (not just markup)
            if line_stripped and not self.is_markup_only(line_stripped):
                current_paragraph.append(line_stripped)
        
        # Don't forget the last paragraph
        if current_paragraph:
            paragraph_text = ' '.join(current_paragraph).strip()
            if len(paragraph_text) > 100:
                paragraphs.append(paragraph_text)
        
        return paragraphs
    
    def clean_markdown(self, text):
        """Remove basic markdown formatting for cleaner display"""
        # Remove bold and italic markers
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
        text = re.sub(r'__(.*?)__', r'\1', text)      # Bold alternative
        text = re.sub(r'_(.*?)_', r'\1', text)        # Italic alternative
        
        # Remove inline code markers
        text = re.sub(r'`(.*?)`', r'\1', text)
        
        # Remove wiki-style links [[link]]
        text = re.sub(r'\[\[(.*?)\]\]', r'\1', text)
        
        # Remove standard markdown links [text](url)
        text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
        
        return text
    
    def get_obsidian_uri(self, file_path):
        """Generate an Obsidian URI to open the file"""
        # Use absolute path approach which is more reliable
        import urllib.parse
        absolute_path = str(file_path.absolute())
        encoded_path = urllib.parse.quote(absolute_path)
        
        return f"obsidian://open?path={encoded_path}"
        """Remove basic markdown formatting for cleaner display"""
        # Remove bold and italic markers
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
        text = re.sub(r'__(.*?)__', r'\1', text)      # Bold alternative
        text = re.sub(r'_(.*?)_', r'\1', text)        # Italic alternative
        
        # Remove inline code markers
        text = re.sub(r'`(.*?)`', r'\1', text)
        
        # Remove wiki-style links [[link]]
        text = re.sub(r'\[\[(.*?)\]\]', r'\1', text)
        
        # Remove standard markdown links [text](url)
        text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
        
        return text
    
    def get_random_quote(self):
        """Get a random paragraph from a random book note"""
        markdown_files = self.get_markdown_files()
        
        if not markdown_files:
            return "No markdown files found in the Books directory!"
        
        # Try up to 10 files to find one with good content
        attempts = 0
        while attempts < 10:
            random_file = random.choice(markdown_files)
            
            try:
                with open(random_file, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                book_title = self.extract_book_title(content)
                paragraphs = self.extract_paragraphs(content)
                
                if paragraphs:
                    random_paragraph = random.choice(paragraphs)
                    clean_paragraph = self.clean_markdown(random_paragraph)
                    obsidian_uri = self.get_obsidian_uri(random_file)
                    
                    return {
                        'quote': clean_paragraph,
                        'book': book_title,
                        'file': random_file.name,
                        'obsidian_link': obsidian_uri
                    }
                    
            except Exception as e:
                print(f"Error reading {random_file}: {e}")
            
            attempts += 1
        
        return "No suitable content found in your book notes."
    
    def display_quote(self):
        """Display a formatted random quote"""
        result = self.get_random_quote()
        
        if isinstance(result, dict):
            print("=" * 80)
            print(f"\n📚 From: {result['book']}")
            print(f"📄 File: {result['file']}")
            print(f"🔗 Open in Obsidian: {result['obsidian_link']}")
            print("\n" + "─" * 80)
            print(f"\n{result['quote']}")
            print("\n" + "─" * 80)
            print()
        else:
            print(result)

def main():
    # Hardcoded path to the Books directory
    books_path = "/Users/catherinepope/CP/Readwise/Books"
    
    try:
        quote_display = ObsidianQuoteDisplay(books_path)
        
        print("\n🎲 Random Quote from Your Book Notes:")
        quote_display.display_quote()
        
        # Option to get more quotes
        while True:
            choice = input("\nWould you like another quote? (y/n): ").lower()
            if choice in ['y', 'yes']:
                print("\n" + "="*80)
                quote_display.display_quote()
            else:
                print("Happy reading! 📖")
                break
                
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Make sure the path to your Books directory is correct.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
