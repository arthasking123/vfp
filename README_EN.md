
# Video Formalization Processor

## Overview
The Video Formalization Processor is a versatile Python application designed for processing lecture videos and corresponding PDF documents. It combines video and document content to produce text-image mixed articles, suitable for conference records and educational content organization.

## Features
- **Video Processing**: Load speaker video files.
- **Document Handling**: Load PDF documents related to video content.
- **Subtitle Generation**: Automatically generate SRT subtitles, allowing user corrections in the edit box.
- **Text-Image Mixing**: Support inserting PDF pages into the subtitle edit box.
- **Find and Replace**: Support using Ctrl+F for search and Ctrl+H for replace, allowing users to quickly locate and modify text content.
- **Document Saving**: Save edited content as HTML documents for subsequent loading and editing.
- **Formalization**: Convert edited content into standardized WORD documents.

## Installation
Clone this repository and install the necessary dependencies.

```bash
git clone https://github.com/arthasking123/vfp.git
cd vfp
pip install -r requirements.txt
```

## Usage
1. **Load Video**: Select and load the speaker's video file.
2. **Load PDF Document**: Load the corresponding PDF format lecture document.
3. **Generate Subtitles**: Click the "Generate Subtitles" button to automatically generate and display subtitles in the right edit box. Users can edit and correct subtitles here.
4. **Edit Subtitles**: During video playback, the background color of the corresponding subtitle line turns yellow for easy location and correction.
5. **Insert PDF Content**: Double-click the displayed PDF pages on the left to insert them into the right edit box.
6. **Save HTML Document**: Click the "Save HTML Document" button to temporarily save the content in the edit box.
7. **Load HTML Document**: Click the "Load HTML Document" button to load previously saved content.
8. **Formalization**: Select the API provider's API, such as OpenAI, and enter the APIKEY. Click the "Formalization" button to convert the edited content into a WORD document.

## Contribution
Contributions to the Video Formalization Processor are welcome. Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add some feature'`).
4. Push the changes to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.
