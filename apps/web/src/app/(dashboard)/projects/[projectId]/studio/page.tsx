import { redirect } from 'next/navigation';

export default function StudioPage({ params }: { params: { projectId: string } }) {
  redirect(`/projects/${params.projectId}/studio/build`);
}
