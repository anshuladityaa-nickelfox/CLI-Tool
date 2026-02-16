# Next.js Component Generation Troubleshooting

## Current Issue
AI-generated React components have syntax errors: "Unexpected token. Expected jsx identifier"

## Root Cause
The AI (Llama 3.3 70B) is not consistently generating valid React/JSX syntax despite explicit prompts.

## Fixes Applied

### 1. Improved Prompts
- Made component structure requirements explicit with line-by-line format
- Added example structure in prompt
- Emphasized CRITICAL REQUIREMENTS

### 2. Post-Processing Validation
- Auto-adds `'use client'` directive if missing
- Auto-adds `import React from 'react'` if missing
- Validates export default exists
- Fixes component structure with `_fix_react_component()` method

### 3. Temperature Adjustment
- Increased temperature from 0.0 to 0.1 for Next.js/NestJS to get better structure variety

## Testing Steps

1. **Generate a fresh Next.js project:**
   ```bash
   NFXinit
   # Select: 2. Next.js
   # Choose: 1 (Button only - simplest component)
   ```

2. **Check generated files:**
   ```bash
   cd your-project
   cat src/components/Button/component.tsx
   ```

3. **Verify structure:**
   - Should start with `'use client';`
   - Should have `import React from 'react';`
   - Should have `export default function Button() {`
   - Should have valid JSX with single root element

4. **Install and test:**
   ```bash
   npm install
   npm run dev
   ```

5. **Visit:**
   - http://localhost:3000 (home page)
   - http://localhost:3000/components (demo page)

## Alternative Solutions

### Option 1: Use Templates for Base Components
Instead of AI generation, use pre-built templates for common components:
- Button: Simple button with variants
- Table: Basic table with props
- Header/Footer: Standard layout components

### Option 2: Different AI Model
Try a different model that's better at code generation:
- GPT-4 (OpenAI)
- Claude 3.5 Sonnet (Anthropic)
- Codestral (Mistral)

### Option 3: Simpler Components
Generate minimal components and let users extend them:
```tsx
'use client';
import React from 'react';

export default function ComponentName() {
  return (
    <div className="p-4">
      <p>ComponentName - Edit this component</p>
    </div>
  );
}
```

## Manual Fix for Existing Projects

If you have a project with broken components:

1. **Open the component file** (e.g., `src/components/LoginPage/component.tsx`)

2. **Ensure it starts with:**
   ```tsx
   'use client';
   
   import React from 'react';
   ```

3. **Ensure proper function structure:**
   ```tsx
   export default function LoginPage() {
     // hooks here
     
     return (
       <div>
         {/* JSX content */}
       </div>
     );
   }
   ```

4. **Check for:**
   - Single root element in return statement
   - Proper closing tags
   - Valid JSX syntax (className not class, etc.)

## Recommended Approach

For production use, I recommend:

1. **Use AI for Django** (works well with current setup)
2. **Use templates for Next.js base components** with AI for customization
3. **Or switch to a more code-focused AI model** for Next.js generation

The current Llama 3.3 70B model works excellently for Django/Python but struggles with consistent React/JSX syntax generation.
