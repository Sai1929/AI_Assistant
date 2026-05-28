import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        paper:      '#F5EFE3',
        'paper-deep': '#EBE3D2',
        card:       '#FBF7EE',
        ink: {
          DEFAULT: '#14283D',
          soft:    '#3A4A60',
        },
        muted:    '#8A7E6A',
        gold: {
          DEFAULT: '#B8881A',
          soft:    '#E8D89A',
        },
        sienna:  '#8B5A2B',
        rule:    '#D9CFB8',
        success: '#3F6B3A',
        warning: '#A66218',
        error:   '#9B3232',
      },
      fontFamily: {
        display: ['var(--font-display)', 'Georgia', 'serif'],
        body:    ['var(--font-body)',    'Georgia', 'serif'],
        ui:      ['var(--font-ui)',      'system-ui', 'sans-serif'],
        mono:    ['var(--font-mono)',    'ui-monospace', 'monospace'],
      },
      letterSpacing: {
        eyebrow: '0.18em',
      },
      borderRadius: {
        hairline: '2px',
        sm:       '4px',
        md:       '8px',
        pill:     '999px',
      },
      boxShadow: {
        soft:  '0 1px 2px rgba(20, 40, 61, 0.04)',
        modal: '0 20px 60px rgba(0, 0, 0, 0.3)',
      },
    },
  },
  plugins: [],
};

export default config;
