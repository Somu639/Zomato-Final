interface AlertProps {
  variant?: "info" | "warning" | "error";
  children: React.ReactNode;
}

export default function Alert({ variant = "info", children }: AlertProps) {
  return <div className={`alert alert--${variant}`}>{children}</div>;
}
