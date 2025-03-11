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

# Check if running on macOS
IS_MACOS=false
if [[ "$OSTYPE" == "darwin"* ]]; then
    IS_MACOS=true
    echo -e "${BLUE}Detected macOS system${NC}"
    
    # Check for Homebrew
    if ! command -v brew &> /dev/null; then
        echo -e "${YELLOW}Homebrew is not installed. It's recommended for managing dependencies on macOS.${NC}"
        echo -e "Install Homebrew with:"
        echo -e "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        read -p "Would you like to install Homebrew now? [y/N]: " INSTALL_BREW
        if [[ $INSTALL_BREW =~ ^[Yy] ]]; then
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
    fi
fi

# Check Python version
echo -e "${BLUE}Checking prerequisites...${NC}"
if ! command -v python3 &> /dev/null; then
    if [ "$IS_MACOS" = true ]; then
        echo -e "${YELLOW}Python 3 not found. Installing via Homebrew...${NC}"
        brew install python@3.9
    else
        echo -e "${RED}Python 3 is required but not installed. Please install Python 3.9 or higher and try again.${NC}"
        exit 1
    fi
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    echo -e "${RED}Python 3.9 or higher is required. You have $PYTHON_VERSION.${NC}"
    if [ "$IS_MACOS" = true ]; then
        echo -e "To upgrade Python on macOS, use:"
        echo -e "brew install python@3.9"
    fi
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

# Check Git installation
if ! command -v git &> /dev/null; then
    if [ "$IS_MACOS" = true ]; then
        echo -e "${YELLOW}Git not found. Installing via Homebrew...${NC}"
        brew install git
    else
        echo -e "${RED}Git is required but not installed. Please install Git and try again.${NC}"
        exit 1
    fi
fi

GIT_VERSION=$(git --version | awk '{print $3}')
echo -e "${GREEN}✓ Git $GIT_VERSION${NC}"

# Determine installation location
echo ""
echo -e "${BLUE}Installation Location${NC}"
echo -e "${YELLOW}Note: The AI Archives should be installed OUTSIDE of your coding projects${NC}"

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

# Ask about virtual environment
echo ""
echo -e "${BLUE}Python Environment Setup${NC}"
echo "The AI Archives system can use either your system Python or a virtual environment."
echo "Using a virtual environment is recommended to avoid conflicts with other Python packages."
echo ""
read -p "Would you like to create a virtual environment? [Y/n]: " CREATE_VENV

USE_VENV=true
if [[ $CREATE_VENV =~ ^[Nn] ]]; then
    USE_VENV=false
    echo "Using system Python. Dependencies will be installed with --user flag."
fi

cd "$INSTALL_PATH"

if [ "$USE_VENV" = true ]; then
    # Set up virtual environment
    echo ""
    echo -e "${BLUE}Setting up Python virtual environment...${NC}"

    # Remove any existing virtual environments
    if [ -d ".venv" ]; then
        echo -e "${YELLOW}Removing existing virtual environment...${NC}"
        rm -rf .venv
    fi

    # Create new virtual environment
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"

    # Activate virtual environment
    source .venv/bin/activate
    echo -e "${GREEN}✓ Virtual environment activated${NC}"

    # Upgrade pip
    python -m pip install --upgrade pip

    # Install dependencies
    echo ""
    echo -e "${BLUE}Installing dependencies...${NC}"
    pip install -r requirements.txt
    
    # Create activation script
    echo ""
    echo -e "${BLUE}Creating activation script...${NC}"
    cat > activate_archives.sh << 'EOL'
#!/bin/bash
# Activate AI Archives environment
source .venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
echo "AI Archives environment activated"
EOL
    chmod +x activate_archives.sh
else
    # Install with --user flag
    echo ""
    echo -e "${BLUE}Installing dependencies to user space...${NC}"
    python3 -m pip install --user -r requirements.txt
    
    # Create activation script that just sets PYTHONPATH
    echo ""
    echo -e "${BLUE}Creating environment script...${NC}"
    cat > activate_archives.sh << 'EOL'
#!/bin/bash
# Set up AI Archives environment
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
echo "AI Archives environment set up"
EOL
    chmod +x activate_archives.sh
fi

# Prompt for data directory location
echo ""
echo -e "${BLUE}Data Directory Setup${NC}"
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
if [ "$USE_VENV" = true ]; then
    python scripts/setup.py --setup-data --data-path "$DATA_PATH"
else
    python3 scripts/setup.py --setup-data --data-path "$DATA_PATH"
fi

# Ask about linking to projects
echo ""
echo -e "${BLUE}Project Integration${NC}"
echo "You can link the AI Archives to your existing projects."
echo "This will create a symbolic link and a .cursorrules file in your project directory."
echo "This is the ONLY change made to your project - no dependencies or virtual environments are installed there."
echo ""
read -p "Would you like to link AI Archives to a project? [y/N]: " LINK_PROJECT

if [[ $LINK_PROJECT =~ ^[Yy] ]]; then
    read -p "Enter the path to your project: " PROJECT_PATH
    if [ -d "$PROJECT_PATH" ]; then
        # Create symbolic link
        echo "Creating symbolic link in $PROJECT_PATH..."
        ln -sf "$INSTALL_PATH" "$PROJECT_PATH/ai.archives"
        
        # Generate cursorrules file
        echo "Generating .cursorrules file in $PROJECT_PATH..."
        if [ "$USE_VENV" = true ]; then
            python scripts/setup.py --link "$PROJECT_PATH"
        else
            python3 scripts/setup.py --link "$PROJECT_PATH"
        fi
        
        echo -e "${GREEN}✓ Project integration complete${NC}"
    else
        echo -e "${RED}Project directory not found: $PROJECT_PATH${NC}"
        echo "You can link to your project later with:"
        echo "  cd $INSTALL_PATH"
        if [ "$USE_VENV" = true ]; then
            echo "  source .venv/bin/activate"
        fi
        echo "  python scripts/setup.py --link /path/to/your/project"
    fi
fi

# Display success message and next steps
echo ""
echo -e "${GREEN}AI Archives successfully installed!${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"

if [ "$USE_VENV" = true ]; then
    echo "1. Activate the environment:"
    echo "   cd $INSTALL_PATH"
    echo "   source activate_archives.sh"
    echo ""
    echo "2. Add content to your archives:"
    echo "   python scripts/archives_cli.py add --project=frontend --section=setup --title=\"Project Setup\" --content=\"...\""
else
    echo "1. Set up the environment:"
    echo "   cd $INSTALL_PATH"
    echo "   source activate_archives.sh"
    echo ""
    echo "2. Add content to your archives:"
    echo "   python3 scripts/archives_cli.py add --project=frontend --section=setup --title=\"Project Setup\" --content=\"...\""
fi

echo ""
echo "3. Search your archives:"
if [ "$USE_VENV" = true ]; then
    echo "   python scripts/archives_cli.py quick-search \"your search query\""
else
    echo "   python3 scripts/archives_cli.py quick-search \"your search query\""
fi

echo ""
echo "4. For your coding projects, you only need to:"
echo "   - Create a symbolic link: ln -s $INSTALL_PATH /path/to/your/project/ai.archives"
echo "   - Generate a .cursorrules file: ./ai.archives/run_archives.sh generate"
echo ""
echo "For more information, see the README.md and INTEGRATION_GUIDE.md files." 