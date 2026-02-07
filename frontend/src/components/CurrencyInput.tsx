interface Props {
  value: number | string;
  onChange: (value: number) => void;
  currency?: string;
  className?: string;
}

export default function CurrencyInput({ value, onChange, currency = 'USD', className = '' }: Props) {
  return (
    <div className={`relative ${className}`}>
      <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm">
        {currency}
      </span>
      <input
        type="number"
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
        className="w-full pl-12 pr-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
      />
    </div>
  );
}
