#!/bin/bash
# AI Archives Installation Script

set -e  # Exit on error

# Colors for prettier output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== AI Archives System Installation ===${NC}"
echo ""
echo -e "This script will install the AI Archives system, which provides a way for AI agents"
echo -e "to maintain knowledge across sessions and effectively work across multiple projects."
echo ""

# Check Python version
echo -e "${BLUE}Checking prerequisites...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is required but not installed. Please install Python 3.8 or higher and try again.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo -e "${RED}Python 3.8 or higher is required. You have $PYTHON_VERSION.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

# Check Git installation
if ! command -v git &> /dev/null; then
    echo -e "${RED}Git is required but not installed. Please install Git and try again.${NC}"
    exit 1
fi

GIT_VERSION=$(git --version | awk '{print $3}')
echo -e "${GREEN}✓ Git $GIT_VERSION${NC}"

# Determine installation location
echo ""
echo -e "${BLUE}Installation Location${NC}"
echo -e "${YELLOW}IMPORTANT: The AI Archives should be installed OUTSIDE of any existing Git projects${NC}"

# Get current directory
CURRENT_DIR=$(pwd)

# Check if current directory is inside a git repository
GIT_ROOT=""
if git rev-parse --is-inside-work-tree &> /dev/null; then
    GIT_ROOT=$(git rev-parse --show-toplevel)
    echo -e "${YELLOW}Warning: You are currently inside a Git repository at:${NC}"
    echo "  $GIT_ROOT"
    echo -e "${YELLOW}Installing AI Archives here may cause Git conflicts.${NC}"
    echo ""
fi

# Suggest installation location
if [ -n "$GIT_ROOT" ]; then
    # Suggest parent directory of current git repo
    PARENT_DIR=$(dirname "$GIT_ROOT")
    DEFAULT_INSTALL="$PARENT_DIR/ai.archives"
else
    # Suggest ~/ai-systems if not in a git repo
    DEFAULT_INSTALL="$HOME/ai-systems/ai.archives"
fi

echo -e "Recommended installation location: ${GREEN}$DEFAULT_INSTALL${NC}"
echo -e "This location is separate from your existing projects."
echo ""
read -p "Where would you like to install AI Archives? [$DEFAULT_INSTALL]: " INSTALL_PATH

if [ -z "$INSTALL_PATH" ]; then
    INSTALL_PATH="$DEFAULT_INSTALL"
fi

# Make sure parent directory exists
PARENT_DIR=$(dirname "$INSTALL_PATH")
mkdir -p "$PARENT_DIR"

# Check if installation directory already exists
if [ -d "$INSTALL_PATH" ]; then
    echo -e "${YELLOW}Directory already exists at $INSTALL_PATH${NC}"
    read -p "Do you want to use the existing directory? [Y/n]: " USE_EXISTING
    if [ -z "$USE_EXISTING" ] || [[ $USE_EXISTING =~ ^[Yy] ]]; then
        echo "Using existing directory."
    else
        echo "Installation aborted."
        exit 1
    fi
else
    echo -e "Installing to: ${GREEN}$INSTALL_PATH${NC}"
    
    # Clone repository
    echo ""
    echo -e "${BLUE}Cloning repository...${NC}"
    git clone https://github.com/tylerqr/ai.archives.git "$INSTALL_PATH"
    echo -e "${GREEN}✓ Repository cloned successfully${NC}"
fi

# Prompt for data directory location
echo "The AI Archives system needs a location to store your archives."
echo "This should be a directory that won't be synced to version control."
echo

DEFAULT_DATA_PATH="$INSTALL_PATH/archives"
read -p "Where would you like to store your archives data? [$DEFAULT_DATA_PATH]: " DATA_PATH

if [ -z "$DATA_PATH" ]; then
    DATA_PATH="$DEFAULT_DATA_PATH"
fi

echo "Setting up archives at: $DATA_PATH"
echo

# Set up the AI Archives
echo ""
echo -e "${BLUE}Setting up AI Archives...${NC}"
cd "$INSTALL_PATH"
python3 scripts/setup.py --setup-data --data-path "$DATA_PATH"

# Ask about linking to projects
echo ""
echo -e "${BLUE}Project Integration${NC}"
echo "You can link the AI Archives to your existing projects."
echo "This will create a .cursorrules file in your project directory"
echo "that instructs AI agents how to interact with the archives."
echo ""
read -p "Would you like to link AI Archives to a project? [y/N]: " LINK_PROJECT

if [[ $LINK_PROJECT =~ ^[Yy] ]]; then
    read -p "Enter the path to your project: " PROJECT_PATH
    if [ -d "$PROJECT_PATH" ]; then
        python3 scripts/setup.py --link "$PROJECT_PATH"
    else
        echo -e "${RED}Project directory not found: $PROJECT_PATH${NC}"
        echo "You can link to your project later with:"
        echo "  cd $INSTALL_PATH"
        echo "  python scripts/setup.py --link /path/to/your/project"
    fi
fi

# Display success message and next steps
echo ""
echo -e "${GREEN}AI Archives successfully installed!${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "1. Add content to your archives:"
echo "   cd $INSTALL_PATH"
echo "   python scripts/archives_cli.py add --project=frontend --section=setup --title=\"Project Setup\" --content=\"...\""
echo ""
echo "2. Search your archives:"
echo "   python scripts/archives_cli.py quick-search \"your search query\""
echo ""
echo "3. Generate .cursorrules file (after updating custom rules):"
echo "   python scripts/integrate_cursorrules.py"
echo ""
echo "For more information, see the README.md and INTEGRATION_GUIDE.md files." 