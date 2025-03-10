module.exports = {
  content: [
    './src/**/*.html',
    './src/**/*.tsx',
    './src/**/*.ts',
    './src/**/*.js',
    './src/**/*.jsx',
    './src-tauri/**/*.rs', // Include Tauri files if needed
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('daisyui'),
  ],

  daisyui: {
    themes: [
      {
        mytheme: {
          "primary": "#5b21b6",
          "secondary": "#db2777",
          "accent": "#f59e0b",
          "neutral": "#374151",
          "base-100": "#111827",
          "info": "#facc15",
          "success": "#10b981",
          "warning": "#fb923c",
          "error": "#ef4444",
          },
        },
      ],
  }
};
