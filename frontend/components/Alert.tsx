interface AlertProps {
  variant?: "info" | "warning" | "error";
  children: React.ReactNode;
}

export default function Alert({ variant = "info", children }: AlertProps) {
  const role = variant === "error" ? "alert" : "status";
  return (
    <div className={`alert alert--${variant}`} role={role}>
      {children}
    </div>
  );
}
