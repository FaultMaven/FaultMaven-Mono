import NextLink from 'next/link'

interface LinkProps extends React.AnchorHTMLAttributes<HTMLAnchorElement> {
  href: string
  children: React.ReactNode
}

export default function Link({ href, children, ...props }: LinkProps) {
  return (
    <NextLink 
      href={href}
      className="text-blue-600 hover:text-blue-800 transition-colors"
      {...props}
    >
      {children}
    </NextLink>
  )
}
