---
name: Premium Nightlife & Dining
colors:
  surface: '#0f1419'
  surface-dim: '#0f1419'
  surface-bright: '#353a3f'
  surface-container-lowest: '#0a0f14'
  surface-container-low: '#171c21'
  surface-container: '#1b2025'
  surface-container-high: '#252a30'
  surface-container-highest: '#30353b'
  on-surface: '#dee3ea'
  on-surface-variant: '#c0c7d4'
  inverse-surface: '#dee3ea'
  inverse-on-surface: '#2c3136'
  outline: '#8a919d'
  outline-variant: '#404752'
  surface-tint: '#9fcaff'
  primary: '#9fcaff'
  on-primary: '#003259'
  primary-container: '#3d9cf5'
  on-primary-container: '#003259'
  inverse-primary: '#0061a5'
  secondary: '#bec7db'
  on-secondary: '#283140'
  secondary-container: '#3e4758'
  on-secondary-container: '#acb5c9'
  tertiary: '#ffb86c'
  on-tertiary: '#492900'
  tertiary-container: '#da8400'
  on-tertiary-container: '#492900'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#d2e4ff'
  primary-fixed-dim: '#9fcaff'
  on-primary-fixed: '#001d36'
  on-primary-fixed-variant: '#00497e'
  secondary-fixed: '#dae3f7'
  secondary-fixed-dim: '#bec7db'
  on-secondary-fixed: '#131c2a'
  on-secondary-fixed-variant: '#3e4758'
  tertiary-fixed: '#ffdcbc'
  tertiary-fixed-dim: '#ffb86c'
  on-tertiary-fixed: '#2c1700'
  on-tertiary-fixed-variant: '#683c00'
  background: '#0f1419'
  on-background: '#dee3ea'
  surface-variant: '#30353b'
typography:
  headline-xl:
    fontFamily: Inter
    fontSize: 40px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  headline-sm:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: '1.4'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1'
    letterSpacing: 0.05em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '700'
    lineHeight: '1.2'
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 16px
  lg: 24px
  xl: 32px
  container-max: 1200px
  gutter: 16px
  margin-mobile: 16px
  margin-desktop: 40px
---

## Brand & Style

The visual identity of the design system is anchored in a "Midnight Premium" aesthetic. It targets discerning diners who value precision, exclusivity, and a high-end digital experience. The interface evokes the feeling of a dimly lit, upscale lounge—sophisticated, calm, and effortlessly modern. 

By utilizing a **Corporate Modern** foundation infused with subtle **Glassmorphism**, the design system prioritizes content legibility against high-contrast backgrounds. The style is intentionally restrained, using the primary blue accent sparingly to guide the user's eye toward calls to action and key discovery moments. The overall emotional response should be one of reliability and "insider" access.

## Colors

This design system utilizes a deep, multi-layered dark palette to create depth without relying on pure blacks. 

- **Foundation:** The base background is a deep charcoal (#0F1419), providing a high-contrast canvas for white and blue elements.
- **Elevation:** Secondary surfaces use a Dark Navy (#1A2332) to distinguish interactive areas from the background.
- **Accents:** The Electric Blue (#3D9CF5) is the core interactive color, used for primary buttons, active states, and focus indicators. 
- **Semantics:** Warning Amber and Error Red are calibrated for high visibility against dark backgrounds, ensuring critical information is never missed.

## Typography

The typography system relies exclusively on **Inter**, a clean, geometric sans-serif that ensures maximum readability across varied screen densities. 

- **Hierarchies:** We use tight line heights for headlines to maintain a modern, "compact" feel, while body text uses a more generous 1.6x line height to prevent eye fatigue in dark mode.
- **Contrast:** Primary information uses "Off-White" (#F8FAFC), while secondary descriptions and metadata use "Muted Gray-Blue" (#8B9CB3) to create a clear visual scale.
- **Labels:** Small labels and badges utilize uppercase styling with increased letter spacing for a refined, utilitarian look.

## Layout & Spacing

The design system employs a strict 8px grid. All spatial relationships—padding, margins, and component heights—should be multiples of 8 (or 4 for micro-adjustments).

- **Grid System:** A 12-column fluid grid is used for desktop layouts, transitioning to a single-column stack on mobile devices.
- **Margins:** A 16px safe area is maintained on mobile screens, increasing to 40px or auto-centering on desktop to maintain a premium, airy feel.
- **Rhythm:** Vertical rhythm is driven by the `lg` (24px) unit for section spacing and `md` (16px) for internal component spacing.

## Elevation & Depth

In a dark theme, depth is communicated through tonal shifts rather than heavy shadows.

- **Surface Tiers:** The background (#0F1419) is the lowest level. Content cards and panels sit on the next level using the Dark Navy (#1A2332). 
- **Outlines:** Instead of traditional shadows, use 1px subtle borders (#2D3A4F) to define the boundaries of elevated elements.
- **Focus States:** High-elevation components like modals or dropdowns may use a soft, diffused 20% opacity blue shadow to indicate they are floating above the main UI.

## Shapes

The shape language is sophisticated and functional, using varying radii to distinguish between containers and interactive elements.

- **Panels & Cards:** Use a larger radius (10px) to give the application a modern, friendly, yet structured feel.
- **Buttons & Inputs:** Use a tighter radius (6px) for interactive controls to signify precision and utility.
- **Badges:** Rank badges and small tags should use a fully rounded (pill) shape to contrast against the more architectural card shapes.

## Components

### Buttons
- **Primary:** Solid #3D9CF5 background with white text. 
- **Loading State:** Replace text with a centered spinner; the button remains at 70% opacity and is non-clickable.
- **Secondary:** Transparent background with a #2D3A4F border and #F8FAFC text.

### Form Controls
- **Inputs/Textarea:** Background set to #1A2332 with a #2D3A4F border. On focus, the border shifts to #3D9CF5 with a subtle outer glow.
- **Toggle/Checkbox:** Uses the primary blue for the "active" state. Transitions should be smooth (200ms ease-in-out).
- **Error State:** Border changes to #F87171 with a small helper text below the field in the same color.

### Recommendation Cards
- **Structure:** 10px corner radius, #1A2332 background.
- **Rank Badge:** Positioned in the top-left corner, featuring a high-contrast background (Primary Blue or Amber) to highlight the restaurant's rating or rank.
- **Image:** Top-aligned with a subtle gradient overlay at the bottom to ensure white text remains legible over the imagery.

### Alert Banners
- **Styling:** Full-width or toast-style. Use low-opacity tints of the semantic colors (e.g., 10% red for error) for the background, but keep a solid 2px left-border of the core semantic color for impact.