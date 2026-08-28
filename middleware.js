export const config = {
  matcher: '/curriculum/:path*',
};

const USERNAME = 'steven';
const PASSWORD = 'ThisShouldSeeTheWorld';

export default function middleware(request) {
  const auth = request.headers.get('authorization');
  if (auth) {
    const [scheme, encoded] = auth.split(' ');
    if (scheme === 'Basic' && encoded) {
      const decoded = atob(encoded);
      const [user, pass] = decoded.split(':');
      if (user === USERNAME && pass === PASSWORD) {
        return;
      }
    }
  }
  return new Response('Authentication required', {
    status: 401,
    headers: { 'WWW-Authenticate': 'Basic realm="Studio Malibu Preview"' },
  });
}
