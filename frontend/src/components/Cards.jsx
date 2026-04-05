// One reusable Card component
export function Card({ children, className = '', variant = 'default' }) {
  return (
    <div className={`card card--${variant} ${className}`}>
      {children}
    </div>
  );
}
