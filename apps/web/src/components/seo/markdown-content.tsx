import Markdown from "react-markdown";

type MarkdownContentProps = {
  content: string;
};

/** Renders pSEO markdown on light canvas with DESIGN.md prose styles */
export function MarkdownContent({ content }: MarkdownContentProps) {
  return (
    <div className="prose-seo max-w-none">
      <Markdown
        components={{
          h2: ({ children }) => <h2>{children}</h2>,
          h3: ({ children }) => <h3>{children}</h3>,
          p: ({ children }) => <p>{children}</p>,
          ul: ({ children }) => <ul>{children}</ul>,
          ol: ({ children }) => <ol>{children}</ol>,
          li: ({ children }) => <li>{children}</li>,
          strong: ({ children }) => <strong>{children}</strong>,
          a: ({ href, children }) => (
            <a href={href} target="_blank" rel="noopener noreferrer">
              {children}
            </a>
          ),
        }}
      >
        {content}
      </Markdown>
    </div>
  );
}
